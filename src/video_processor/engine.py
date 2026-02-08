from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import os
import queue
import subprocess
import threading
import time
from typing import Callable, Iterable

from .config import AppConfig
from .ffmpeg import MediaInfo, build_ffmpeg_command, check_ffmpeg, progress_from_out_time, probe_media
from .logging import BatchLogger


STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
STATUS_CANCELED = "canceled"


@dataclass
class WorkItem:
    id: int
    input_path: str
    output_path: str
    status: str = STATUS_QUEUED
    progress: int | None = 0
    message: str = ""
    error: str = ""
    start_time: float | None = None
    end_time: float | None = None
    input_bytes: int | None = None
    output_bytes: int | None = None
    media: MediaInfo | None = None
    output_media: MediaInfo | None = None
    thumbnail_path: str | None = None


@dataclass
class BatchSummary:
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    canceled: int = 0
    queued: int = 0
    running: int = 0


ItemCallback = Callable[[WorkItem], None]
BatchCallback = Callable[[BatchSummary], None]


class BatchHandle:
    def __init__(
        self,
        *,
        items: list[WorkItem],
        work_queue: queue.Queue[WorkItem],
        pause_event: threading.Event,
        cancel_event: threading.Event,
        running_processes: dict[int, subprocess.Popen],
        threads: list[threading.Thread],
        logger: BatchLogger,
        lock: threading.Lock,
        on_item_update: ItemCallback | None,
    ) -> None:
        self.items = items
        self._queue = work_queue
        self._pause_event = pause_event
        self._cancel_event = cancel_event
        self._running_processes = running_processes
        self._threads = threads
        self._logger = logger
        self._lock = lock
        self._on_item_update = on_item_update
        self.csv_path = str(logger.csv_path) if logger.enable_csv else ""
        self.json_path = str(logger.json_path) if logger.enable_json else ""
        self._closed = False

    def pause(self) -> None:
        self._pause_event.clear()

    def resume(self) -> None:
        self._pause_event.set()

    def cancel(self) -> None:
        self._cancel_event.set()
        with self._lock:
            for proc in self._running_processes.values():
                _terminate_process(proc)
        self._mark_queued_canceled()

    def _mark_queued_canceled(self) -> None:
        updated = []
        for item in self.items:
            if item.status == STATUS_QUEUED:
                item.status = STATUS_CANCELED
                item.message = "canceled"
                updated.append(item)
        for item in updated:
            if self._on_item_update:
                self._on_item_update(item)

    def retry_failed(self) -> None:
        with self._lock:
            for item in self.items:
                if item.status == STATUS_FAILED:
                    item.status = STATUS_QUEUED
                    item.progress = 0
                    item.error = ""
                    self._queue.put(item)

    def is_running(self) -> bool:
        return any(t.is_alive() for t in self._threads)

    def wait(self) -> None:
        for t in self._threads:
            t.join()
        if not self._closed:
            self._logger.close()
            self._closed = True


class VideoProcessorEngine:
    def __init__(
        self,
        config: AppConfig,
        *,
        on_item_update: ItemCallback | None = None,
        on_batch_update: BatchCallback | None = None,
    ) -> None:
        self.config = config
        self.on_item_update = on_item_update
        self.on_batch_update = on_batch_update

    def scan_inputs(self) -> list[WorkItem]:
        config = self.config
        input_root = Path(config.input_dir)
        output_root = Path(config.output_dir) if config.output_dir else None
        extensions = set(ext.lower() for ext in config.extensions)
        items: list[WorkItem] = []
        item_id = 1
        for root, _, files in os.walk(input_root):
            for name in files:
                path = Path(root) / name
                if path.suffix.lower() not in extensions:
                    continue
                rel = path.relative_to(input_root)
                out_path = output_root / rel if output_root else None
                status = STATUS_QUEUED
                message = ""
                final_out = out_path
                if out_path:
                    if out_path.exists():
                        if config.collision_policy == "skip":
                            status = STATUS_SKIPPED
                            message = "output exists"
                        elif config.collision_policy == "suffix":
                            final_out = _suffix_path(out_path)
                else:
                    message = "output not set"
                input_bytes = None
                try:
                    input_bytes = path.stat().st_size
                except OSError:
                    input_bytes = None
                items.append(
                    WorkItem(
                        id=item_id,
                        input_path=str(path),
                        output_path=str(final_out) if final_out else "",
                        status=status,
                        message=message,
                        input_bytes=input_bytes,
                    )
                )
                item_id += 1
        return items

    def start_batch(self, items: list[WorkItem]) -> BatchHandle:
        self.config.validate()
        check_ffmpeg()

        pause_event = threading.Event()
        pause_event.set()
        cancel_event = threading.Event()
        work_queue: queue.Queue[WorkItem] = queue.Queue()
        running_processes: dict[int, subprocess.Popen] = {}
        lock = threading.Lock()

        for item in items:
            if item.status == STATUS_QUEUED:
                work_queue.put(item)
            else:
                self._emit_item(item)

        logger = BatchLogger(
            output_dir=self.config.output_dir,
            enable_csv=self.config.enable_csv_log,
            enable_json=self.config.enable_json_log,
            csv_path=self.config.csv_log_path or None,
            json_path=self.config.json_log_path or None,
        )

        def worker_loop() -> None:
            while not cancel_event.is_set():
                pause_event.wait()
                try:
                    item = work_queue.get(timeout=0.2)
                except queue.Empty:
                    break
                if cancel_event.is_set():
                    work_queue.task_done()
                    break
                self._process_item(
                    item,
                    logger=logger,
                    cancel_event=cancel_event,
                    pause_event=pause_event,
                    running_processes=running_processes,
                    lock=lock,
                )
                work_queue.task_done()

        threads: list[threading.Thread] = []
        worker_count = self.config.workers if self.config.parallel else 1
        for _ in range(max(1, worker_count)):
            t = threading.Thread(target=worker_loop, daemon=True)
            t.start()
            threads.append(t)

        handle = BatchHandle(
            items=items,
            work_queue=work_queue,
            pause_event=pause_event,
            cancel_event=cancel_event,
            running_processes=running_processes,
            threads=threads,
            logger=logger,
            lock=lock,
            on_item_update=self.on_item_update,
        )

        monitor = threading.Thread(
            target=self._monitor_batch, args=(items, handle, logger), daemon=True
        )
        monitor.start()

        return handle

    def _process_item(
        self,
        item: WorkItem,
        *,
        logger: BatchLogger,
        cancel_event: threading.Event,
        pause_event: threading.Event,
        running_processes: dict[int, subprocess.Popen],
        lock: threading.Lock,
    ) -> None:
        if cancel_event.is_set():
            item.status = STATUS_CANCELED
            self._emit_item(item)
            return

        item.status = STATUS_RUNNING
        item.start_time = time.time()
        item.progress = 0
        self._emit_item(item)

        input_path = Path(item.input_path)
        output_path = Path(item.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        temp_output = _temp_output_path(output_path)

        try:
            item.input_bytes = input_path.stat().st_size
        except OSError:
            item.input_bytes = None

        if self.config.dry_run:
            item.status = STATUS_SKIPPED
            item.message = "dry-run"
            item.end_time = time.time()
            self._emit_item(item)
            self._log_item(item, logger)
            return

        try:
            item.media = probe_media(input_path)
            if not item.media.duration:
                item.progress = None
        except Exception as exc:
            error_msg = str(exc)
            # Detect corrupted files and provide better error message
            if "moov atom not found" in error_msg.lower() or "invalid data found when processing input" in error_msg.lower():
                item.status = STATUS_FAILED
                item.error = f"File is corrupted or incomplete: {error_msg}"
            else:
                item.status = STATUS_FAILED
                item.error = error_msg
            item.end_time = time.time()
            self._emit_item(item)
            self._log_item(item, logger)
            return

        base_cmd = build_ffmpeg_command(
            input_path,
            temp_output,
            video_codec=self.config.video_codec,
            crf=self.config.crf,
            preset=self.config.preset,
            audio_codec=self.config.audio_codec,
            audio_bitrate_kbps=self.config.audio_bitrate_kbps,
            target_fps=self.config.target_fps,
            overwrite=self.config.collision_policy == "overwrite",
            gpu_type=getattr(self.config, 'gpu_type', 'none'),
            use_gpu=getattr(self.config, 'use_gpu', True),
            use_hw_decode=getattr(self.config, 'use_hw_decode', True),
            copy_audio=getattr(self.config, 'copy_audio', False),
            skip_reencode=getattr(self.config, 'skip_reencode', False),
        )

        cmd = base_cmd[:-1] + ["-progress", "pipe:1", "-loglevel", "error", base_cmd[-1]]
        stderr_lines: list[str] = []

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        with lock:
            running_processes[item.id] = proc

        def read_stderr() -> None:
            if not proc.stderr:
                return
            for line in proc.stderr:
                stderr_lines.append(line.rstrip())

        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()

        try:
            if proc.stdout:
                for line in proc.stdout:
                    if cancel_event.is_set():
                        _terminate_process(proc)
                        break
                    line = line.strip()
                    if not line or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    if key == "out_time_ms":
                        try:
                            out_us = int(value)
                        except ValueError:
                            continue
                        progress = progress_from_out_time(out_us, item.media.duration)
                        if progress is not None and progress != item.progress:
                            item.progress = progress
                            self._emit_item(item)
                    elif key == "progress" and value == "end":
                        item.progress = 100
                        self._emit_item(item)
            proc.wait()
        finally:
            stderr_thread.join(timeout=1)
            _close_pipes(proc)
            with lock:
                running_processes.pop(item.id, None)

        if cancel_event.is_set():
            item.status = STATUS_CANCELED
            item.end_time = time.time()
            _cleanup_partial(temp_output)
            self._emit_item(item)
            self._log_item(item, logger)
            return

        if proc.returncode != 0:
            item.status = STATUS_FAILED
            item.error = "; ".join(stderr_lines).strip() or "ffmpeg failed"
        else:
            item.status = STATUS_COMPLETED
            item.progress = 100

        item.end_time = time.time()
        if item.status == STATUS_COMPLETED:
            try:
                if output_path.exists() and self.config.collision_policy == "overwrite":
                    output_path.unlink()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                temp_output.replace(output_path)
            except OSError as exc:
                item.status = STATUS_FAILED
                item.error = f"Failed to finalize output: {exc}"
                _cleanup_partial(temp_output)
        else:
            _cleanup_partial(temp_output)

        if item.status == STATUS_COMPLETED:
            try:
                item.output_bytes = output_path.stat().st_size
            except OSError:
                item.output_bytes = None

        if item.status == STATUS_COMPLETED:
            try:
                item.output_media = probe_media(output_path)
            except Exception:
                item.output_media = None

        self._emit_item(item)
        self._log_item(item, logger)

    def _log_item(self, item: WorkItem, logger: BatchLogger) -> None:
        timestamp = datetime.utcnow().isoformat()
        processing_seconds = None
        if item.start_time and item.end_time:
            processing_seconds = item.end_time - item.start_time
        logger.record_item(
            timestamp=timestamp,
            input_path=item.input_path,
            output_path=item.output_path,
            status=item.status,
            error_message=item.error,
            media=item.media,
            output_media=item.output_media,
            input_bytes=item.input_bytes,
            output_bytes=item.output_bytes,
            processing_seconds=processing_seconds,
        )

    def _monitor_batch(
        self, items: list[WorkItem], handle: BatchHandle, logger: BatchLogger
    ) -> None:
        handle.wait()
        summary = self._build_summary(items)
        if self.on_batch_update:
            self.on_batch_update(summary)
        if logger.enable_json:
            summary_path = Path(logger.json_path).with_suffix(".summary.json")
            summary_path.write_text(json_dump(summary), encoding="utf-8")

    def _build_summary(self, items: Iterable[WorkItem]) -> BatchSummary:
        summary = BatchSummary()
        for item in items:
            summary.total += 1
            if item.status == STATUS_COMPLETED:
                summary.completed += 1
            elif item.status == STATUS_FAILED:
                summary.failed += 1
            elif item.status == STATUS_SKIPPED:
                summary.skipped += 1
            elif item.status == STATUS_CANCELED:
                summary.canceled += 1
            elif item.status == STATUS_RUNNING:
                summary.running += 1
            elif item.status == STATUS_QUEUED:
                summary.queued += 1
        return summary

    def _emit_item(self, item: WorkItem) -> None:
        if self.on_item_update:
            self.on_item_update(item)


def _suffix_path(path: Path) -> Path:
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _temp_output_path(path: Path) -> Path:
    if path.suffix:
        temp = path.with_name(f"{path.stem}.partial{path.suffix}")
    else:
        temp = path.with_suffix(".partial")
    if not temp.exists():
        return temp
    counter = 1
    while True:
        if path.suffix:
            candidate = path.with_name(f"{path.stem}.partial{counter}{path.suffix}")
        else:
            candidate = path.with_name(f"{path.name}.partial{counter}")
        if not candidate.exists():
            return candidate
        counter += 1


def _terminate_process(proc: subprocess.Popen) -> None:
    try:
        proc.terminate()
    except OSError:
        return
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
        except OSError:
            return


def _close_pipes(proc: subprocess.Popen) -> None:
    for stream in (proc.stdout, proc.stderr, proc.stdin):
        try:
            if stream:
                stream.close()
        except OSError:
            continue


def _cleanup_partial(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        return


def json_dump(summary: BatchSummary) -> str:
    return json.dumps(
        {
            "total": summary.total,
            "completed": summary.completed,
            "failed": summary.failed,
            "skipped": summary.skipped,
            "canceled": summary.canceled,
            "queued": summary.queued,
            "running": summary.running,
        },
        indent=2,
    )
