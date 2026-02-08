from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from ..config import AppConfig, load_ui_settings, save_ui_settings
from ..engine import VideoProcessorEngine
from ..ffmpeg import probe_media
from .extensions_view import ExtensionsView
from .progress_view import ProgressView
from .settings_view import SettingsView
from .theme import apply_dark_theme, apply_light_theme


class AppSignals(QtCore.QObject):
    itemUpdated = QtCore.Signal(object)
    batchUpdated = QtCore.Signal(object)


class ThumbnailSignals(QtCore.QObject):
    finished = QtCore.Signal(int, str)


class ThumbnailTask(QtCore.QRunnable):
    def __init__(self, item_id: int, input_path: str, output_path: str) -> None:
        super().__init__()
        self.item_id = item_id
        self.input_path = input_path
        self.output_path = output_path
        self.signals = ThumbnailSignals()

    def run(self) -> None:
        path = generate_thumbnail(self.input_path, self.output_path)
        self.signals.finished.emit(self.item_id, path)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Video Processor")
        self.resize(1100, 700)

        self.config = AppConfig()
        ui_settings = load_ui_settings()
        if ui_settings.get("theme") in {"dark", "light"}:
            self.config.theme = ui_settings["theme"]

        self.settings_view = SettingsView()
        self.extensions_view = ExtensionsView()
        self.progress_view = ProgressView()

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.progress_view, "Batch")
        self.tabs.addTab(self.settings_view, "Settings")
        self.tabs.addTab(self.extensions_view, "File Extensions")
        self.setCentralWidget(self.tabs)

        self.settings_view.load_config(self.config)
        self.progress_view.set_input_dir(self.config.input_dir)
        self.progress_view.set_output_dir(self.config.output_dir)
        self.settings_view.set_output_dir(self.config.output_dir)
        self._apply_theme(self.config.theme)

        self.signals = AppSignals()
        self.signals.itemUpdated.connect(self._on_item_updated)
        self.signals.batchUpdated.connect(self._on_batch_updated)

        self.settings_view.saveProfileRequested.connect(self._save_profile)
        self.settings_view.loadProfileRequested.connect(self._load_profile)
        self.settings_view.themeChanged.connect(self._on_theme_changed)
        self.progress_view.inputChanged.connect(self._refresh_scan)
        self.progress_view.outputChanged.connect(self._refresh_scan)
        self.progress_view.outputChanged.connect(self._sync_output_dir)
        self.settings_view.startRequested.connect(self._start_from_settings)
        self.extensions_view.extensionsChanged.connect(self._refresh_scan)

        self.progress_view.startRequested.connect(self._start_processing)
        self.progress_view.pauseRequested.connect(self._pause_processing)
        self.progress_view.resumeRequested.connect(self._resume_processing)
        self.progress_view.cancelRequested.connect(self._cancel_processing)
        self.progress_view.retryRequested.connect(self._retry_failed)
        self.progress_view.refreshRequested.connect(self._refresh_scan)
        self.progress_view.openOutputRequested.connect(self._open_output)
        self.progress_view.copyLogRequested.connect(self._copy_log_path)
        self.progress_view.filterChanged.connect(self.progress_view.set_completed_filter)
        self.progress_view.infoRequested.connect(self._show_item_info)

        self.engine: VideoProcessorEngine | None = None
        self.batch_handle = None
        self.items = []
        self.items_by_id = {}
        self.thumbnail_pool = QtCore.QThreadPool.globalInstance()
        self.thumbnail_tasks = set()

    def _collect_config(self) -> AppConfig:
        self.settings_view.apply_to_config(self.config)
        self.config.input_dir = self.progress_view.get_input_dir()
        self.config.output_dir = self.progress_view.get_output_dir()
        self.config.extensions = self.extensions_view.get_extensions()
        self.config.validate()
        return self.config

    def _start_processing(self) -> None:
        try:
            config = self._collect_config()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Invalid Settings", str(exc))
            return
        if not config.input_dir or not config.output_dir:
            QtWidgets.QMessageBox.warning(
                self, "Missing Paths", "Please select input and output folders."
            )
            return
        self.engine = VideoProcessorEngine(
            config,
            on_item_update=self.signals.itemUpdated.emit,
            on_batch_update=self.signals.batchUpdated.emit,
        )
        self.items = self.engine.scan_inputs()
        self.items_by_id = {item.id: item for item in self.items}
        self.progress_view.model.set_items(self.items)
        self._queue_thumbnails()
        if not self.items:
            QtWidgets.QMessageBox.information(
                self, "No Files", "No matching video files were found."
            )
            return
        self.batch_handle = self.engine.start_batch(self.items)
        self.tabs.setCurrentWidget(self.progress_view)

    def _start_from_settings(self) -> None:
        self._start_processing()
        self.tabs.setCurrentWidget(self.progress_view)

    def _refresh_scan(self) -> None:
        if self.batch_handle and self.batch_handle.is_running():
            return
        try:
            config = self._collect_config()
        except Exception:
            return
        if not config.input_dir:
            self.items = []
            self.progress_view.model.set_items(self.items)
            self.progress_view.set_summary("Select an input folder to scan.")
            self.progress_view.set_overall_progress(0)
            return
        engine = VideoProcessorEngine(config)
        self.items = engine.scan_inputs()
        self.items_by_id = {item.id: item for item in self.items}
        self.progress_view.model.set_items(self.items)
        self._queue_thumbnails()
        self._update_summary()

    def _pause_processing(self) -> None:
        if self.batch_handle:
            self.batch_handle.pause()

    def _resume_processing(self) -> None:
        if self.batch_handle:
            self.batch_handle.resume()

    def _cancel_processing(self) -> None:
        if self.batch_handle:
            self.batch_handle.cancel()

    def _retry_failed(self) -> None:
        if self.batch_handle:
            self.batch_handle.retry_failed()

    def _open_output(self) -> None:
        if self.config.output_dir:
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(self.config.output_dir)
            )

    def _copy_log_path(self) -> None:
        if not self.batch_handle:
            return
        path = self.batch_handle.csv_path or self.batch_handle.json_path
        if not path:
            return
        QtWidgets.QApplication.clipboard().setText(path)

    def _show_item_info(self, item) -> None:
        try:
            if item.media is None and Path(item.input_path).exists():
                item.media = probe_media(item.input_path)
            if item.output_path and item.output_media is None and Path(item.output_path).exists():
                item.output_media = probe_media(item.output_path)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, "Metadata Error", str(exc))
            return

        lines = [
            f"Input: {item.input_path}",
            f"Output: {item.output_path}",
        ]
        if item.media:
            lines.extend(
                [
                    "",
                    "Input Metadata:",
                    f"  Duration: {item.media.duration:.2f}s" if item.media.duration else "  Duration: n/a",
                    f"  Resolution: {item.media.width}x{item.media.height}" if item.media.width and item.media.height else "  Resolution: n/a",
                    f"  Video Codec: {item.media.video_codec or 'n/a'}",
                    f"  Audio Codec: {item.media.audio_codec or 'n/a'}",
                    f"  FPS: {item.media.fps:.2f}" if item.media.fps else "  FPS: n/a",
                ]
            )
        if item.output_media:
            lines.extend(
                [
                    "",
                    "Output Metadata:",
                    f"  Duration: {item.output_media.duration:.2f}s" if item.output_media.duration else "  Duration: n/a",
                    f"  Resolution: {item.output_media.width}x{item.output_media.height}" if item.output_media.width and item.output_media.height else "  Resolution: n/a",
                    f"  Video Codec: {item.output_media.video_codec or 'n/a'}",
                    f"  Audio Codec: {item.output_media.audio_codec or 'n/a'}",
                    f"  FPS: {item.output_media.fps:.2f}" if item.output_media.fps else "  FPS: n/a",
                ]
            )
        QtWidgets.QMessageBox.information(self, "Video Info", "\n".join(lines))

    def _queue_thumbnails(self) -> None:
        if not self.config.output_dir:
            return
        cache_dir = _thumbnail_cache_dir(self.config.output_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        for item in self.items:
            if item.thumbnail_path or item.id in self.thumbnail_tasks:
                continue
            input_path = Path(item.input_path)
            if not input_path.exists():
                continue
            thumb_path = cache_dir / _thumbnail_name(input_path)
            if thumb_path.exists():
                item.thumbnail_path = str(thumb_path)
                self.progress_view.model.update_item(item)
                continue
            task = ThumbnailTask(item.id, str(input_path), str(thumb_path))
            task.signals.finished.connect(self._on_thumbnail_ready)
            self.thumbnail_tasks.add(item.id)
            self.thumbnail_pool.start(task)

    def _on_thumbnail_ready(self, item_id: int, path: str) -> None:
        self.thumbnail_tasks.discard(item_id)
        item = self.items_by_id.get(item_id)
        if not item:
            return
        if path and Path(path).exists():
            item.thumbnail_path = path
            self.progress_view.model.update_item(item)

    def _on_item_updated(self, item) -> None:
        self.progress_view.model.update_item(item)
        self._update_summary()

    def _on_batch_updated(self, summary) -> None:
        self._update_summary(final=True, summary=summary)
        self._show_summary_popup()

    def _update_summary(self, final: bool = False, summary=None) -> None:
        total = len(self.items)
        completed = len([i for i in self.items if i.status == "completed"])
        running = len([i for i in self.items if i.status == "running"])
        failed = len([i for i in self.items if i.status == "failed"])
        skipped = len([i for i in self.items if i.status == "skipped"])
        canceled = len([i for i in self.items if i.status == "canceled"])
        queued = len([i for i in self.items if i.status == "queued"])
        label = (
            f"Total: {total}  Completed: {completed}  "
            f"Running: {running}  Failed: {failed}  "
            f"Skipped: {skipped}  Canceled: {canceled}"
        )
        if final:
            label += "  (finished)"
        self.progress_view.set_summary(label)

        if total > 0:
            progress = 0.0
            for item in self.items:
                if item.status == "completed":
                    progress += 1.0
                elif item.status == "running" and item.progress is not None:
                    progress += item.progress / 100.0
            overall = int((progress / total) * 100)
            self.progress_view.set_overall_progress(overall)

        in_progress_count = running + queued
        completed_count = completed + failed + skipped + canceled
        self.progress_view.update_section_titles(
            in_progress_count=in_progress_count,
            completed_count=completed_count,
        )

    def _show_summary_popup(self) -> None:
        if not self.items:
            return
        completed = len([i for i in self.items if i.status == "completed"])
        failed = len([i for i in self.items if i.status == "failed"])
        skipped = len([i for i in self.items if i.status == "skipped"])
        canceled = len([i for i in self.items if i.status == "canceled"])
        total_input = sum(i.input_bytes or 0 for i in self.items if i.input_bytes)
        total_output = sum(i.output_bytes or 0 for i in self.items if i.output_bytes)
        saved_bytes = max(0, total_input - total_output)
        saved_percent = (saved_bytes / total_input * 100.0) if total_input else 0.0
        lines = [
            "Batch complete.",
            f"Completed: {completed}",
            f"Failed: {failed}",
            f"Skipped: {skipped}",
            f"Canceled: {canceled}",
            f"Input total: {total_input / (1024 * 1024):.2f} MB",
            f"Output total: {total_output / (1024 * 1024):.2f} MB",
            f"Saved: {saved_bytes / (1024 * 1024):.2f} MB ({saved_percent:.1f}%)",
        ]
        if self.batch_handle and self.batch_handle.csv_path:
            lines.append(f"CSV Log: {self.batch_handle.csv_path}")
        if self.batch_handle and self.batch_handle.json_path:
            lines.append(f"JSON Log: {self.batch_handle.json_path}")
        QtWidgets.QMessageBox.information(self, "Processing Summary", "\n".join(lines))

    def _save_profile(self) -> None:
        try:
            config = self._collect_config()
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Invalid Settings", str(exc))
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Configuration", filter="JSON Files (*.json)"
        )
        if path:
            config.save_profile(path)

    def _load_profile(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Configuration", filter="JSON Files (*.json)"
        )
        if not path:
            return
        try:
            config = AppConfig.load_profile(path)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, "Load Failed", str(exc))
            return
        self.config = config
        self.settings_view.load_config(self.config)
        self.progress_view.set_input_dir(self.config.input_dir)
        self.progress_view.set_output_dir(self.config.output_dir)
        self.settings_view.set_output_dir(self.config.output_dir)
        self.extensions_view.set_extensions(self.config.extensions)
        self._apply_theme(self.config.theme)
        self._refresh_scan()

    def _sync_output_dir(self) -> None:
        self.settings_view.set_output_dir(self.progress_view.get_output_dir())

    def _on_theme_changed(self, theme: str) -> None:
        self._apply_theme(theme)
        save_ui_settings({"theme": theme})

    def _apply_theme(self, theme: str) -> None:
        if theme == "light":
            apply_light_theme(QtWidgets.QApplication.instance())
        else:
            apply_dark_theme(QtWidgets.QApplication.instance())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.batch_handle and self.batch_handle.is_running():
            dialog = QtWidgets.QProgressDialog(
                "Stopping background tasks...", None, 0, 0, self
            )
            dialog.setWindowTitle("Closing")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.setMinimumDuration(0)
            dialog.setCancelButton(None)
            dialog.show()
            self.batch_handle.cancel()
            try:
                self.thumbnail_pool.clear()
            except AttributeError:
                pass

            # Wait for graceful shutdown with extended timeout
            deadline = time.time() + 5.0
            while self.batch_handle.is_running() and time.time() < deadline:
                QtCore.QCoreApplication.processEvents()
                time.sleep(0.05)

            # Force kill any remaining ffmpeg processes
            self._force_kill_ffmpeg_processes()

            dialog.close()
        else:
            # Even if not running, clean up any orphaned ffmpeg processes
            self._force_kill_ffmpeg_processes()

        event.accept()

    def _force_kill_ffmpeg_processes(self) -> None:
        """Force kill any ffmpeg processes started by this application."""
        import os
        import signal

        try:
            # On Windows, use taskkill to terminate ffmpeg processes
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "ffmpeg.exe"],
                    capture_output=True,
                    timeout=3
                )
            else:
                # On Unix-like systems, kill ffmpeg processes by name
                subprocess.run(
                    ["pkill", "-9", "ffmpeg"],
                    capture_output=True,
                    timeout=3
                )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # Ignore errors if process is already gone or command not found
            pass


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Video Processor")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def _thumbnail_cache_dir(output_dir: str) -> Path:
    return Path(output_dir) / ".video_processor_thumbnails"


def _thumbnail_name(path: Path) -> str:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0
    key = f"{path}|{mtime}"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return f"{digest}.jpg"


def generate_thumbnail(input_path: str, output_path: str) -> str:
    attempts = ["00:00:01.000", "00:00:00.500", "00:00:00.000"]
    for timestamp in attempts:
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            timestamp,
            "-i",
            input_path,
            "-frames:v",
            "1",
            "-vf",
            "scale=160:-1",
            "-q:v",
            "2",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and Path(output_path).exists():
            return output_path
    return ""
