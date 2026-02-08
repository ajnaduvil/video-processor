from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ..config import AppConfig, PRESETS


class SettingsView(QtWidgets.QWidget):
    saveProfileRequested = QtCore.Signal()
    loadProfileRequested = QtCore.Signal()
    themeChanged = QtCore.Signal(str)
    startRequested = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.codec_combo = QtWidgets.QComboBox()
        self.codec_combo.addItems(["h264", "h265"])
        self.codec_combo.setCurrentText("h265")
        self.crf_spin = QtWidgets.QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(23)
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.addItems(PRESETS)

        self.audio_combo = QtWidgets.QComboBox()
        self.audio_combo.addItems(["aac", "opus"])
        self.audio_bitrate = QtWidgets.QSpinBox()
        self.audio_bitrate.setRange(32, 512)
        self.audio_bitrate.setValue(128)

        self.fps_combo = QtWidgets.QComboBox()
        self.fps_combo.addItems(["same", "24", "25", "30", "50", "60"])
        self.fps_combo.setCurrentText("30")

        self.parallel_check = QtWidgets.QCheckBox("Enable parallel processing")
        self.workers_spin = QtWidgets.QSpinBox()
        self.workers_spin.setRange(1, 64)

        self.dry_run_check = QtWidgets.QCheckBox("Dry run (no encoding)")

        self.collision_combo = QtWidgets.QComboBox()
        self.collision_combo.addItems(["skip", "overwrite", "suffix"])

        self.csv_check = QtWidgets.QCheckBox("Enable CSV log")
        self.csv_path_edit = QtWidgets.QLineEdit()
        self.csv_path_edit.setPlaceholderText("Auto in output folder")
        self.csv_browse = QtWidgets.QPushButton("Browse")

        self.json_check = QtWidgets.QCheckBox("Enable JSON log")
        self.json_path_edit = QtWidgets.QLineEdit()
        self.json_path_edit.setPlaceholderText("Auto in output folder")
        self.json_browse = QtWidgets.QPushButton("Browse")

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.currentTextChanged.connect(self.themeChanged.emit)

        self.gpu_type_combo = QtWidgets.QComboBox()
        self.gpu_type_combo.addItems(["none", "nvidia", "amd", "intel", "macos"])
        self.use_gpu_check = QtWidgets.QCheckBox("Use GPU acceleration")
        self.hw_decode_check = QtWidgets.QCheckBox("GPU decode (hardware)")
        self.copy_audio_check = QtWidgets.QCheckBox("Copy audio (no re-encode)")
        self.skip_reencode_check = QtWidgets.QCheckBox("Skip re-encode (stream copy)")

        self.save_profile_button = QtWidgets.QPushButton("Save Config")
        self.load_profile_button = QtWidgets.QPushButton("Load Config")
        self.save_profile_button.clicked.connect(self.saveProfileRequested.emit)
        self.load_profile_button.clicked.connect(self.loadProfileRequested.emit)
        self.start_button = QtWidgets.QPushButton("Start Processing")
        self.start_button.clicked.connect(self.startRequested.emit)
        self.csv_browse.clicked.connect(self._browse_csv)
        self.json_browse.clicked.connect(self._browse_json)
        self._output_dir = ""

        form = QtWidgets.QFormLayout()

        form.addRow("Video codec", self.codec_combo)
        form.addRow("CRF", self.crf_spin)
        form.addRow("Preset", self.preset_combo)
        form.addRow("Audio codec", self.audio_combo)
        form.addRow("Audio bitrate (kbps)", self.audio_bitrate)
        form.addRow("Target FPS", self.fps_combo)
        form.addRow(self.parallel_check, self.workers_spin)
        form.addRow("Collision policy", self.collision_combo)
        form.addRow(self.dry_run_check)

        csv_layout = QtWidgets.QHBoxLayout()
        csv_layout.addWidget(self.csv_path_edit)
        csv_layout.addWidget(self.csv_browse)
        form.addRow(self.csv_check, csv_layout)

        json_layout = QtWidgets.QHBoxLayout()
        json_layout.addWidget(self.json_path_edit)
        json_layout.addWidget(self.json_browse)
        form.addRow(self.json_check, json_layout)

        form.addRow("Theme", self.theme_combo)

        gpu_layout = QtWidgets.QHBoxLayout()
        gpu_layout.addWidget(self.use_gpu_check)
        gpu_layout.addWidget(self.gpu_type_combo)
        form.addRow("GPU Acceleration", gpu_layout)
        form.addRow(self.hw_decode_check)
        form.addRow(self.copy_audio_check)
        form.addRow(self.skip_reencode_check)

        profile_layout = QtWidgets.QHBoxLayout()
        profile_layout.addWidget(self.save_profile_button)
        profile_layout.addWidget(self.load_profile_button)
        profile_layout.addWidget(self.start_button)
        form.addRow(profile_layout)

        self.setLayout(form)

    def _browse_csv(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select CSV Log Path", filter="CSV Files (*.csv)"
        )
        if path:
            self.csv_path_edit.setText(path)

    def _browse_json(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Select JSON Log Path", filter="JSON Lines (*.jsonl)"
        )
        if path:
            self.json_path_edit.setText(path)

    def set_output_dir(self, output_dir: str) -> None:
        self._output_dir = output_dir.strip()
        self._update_log_placeholders()

    def _update_log_placeholders(self) -> None:
        if self._output_dir:
            hint = f"Auto in {self._output_dir}"
        else:
            hint = "Auto in output folder"
        self.csv_path_edit.setPlaceholderText(hint)
        self.json_path_edit.setPlaceholderText(hint)

    def load_config(self, config: AppConfig) -> None:
        self.codec_combo.setCurrentText(config.video_codec)
        self.crf_spin.setValue(config.crf)
        self.preset_combo.setCurrentText(config.preset)
        self.audio_combo.setCurrentText(config.audio_codec)
        self.audio_bitrate.setValue(config.audio_bitrate_kbps)
        self.fps_combo.setCurrentText(str(config.target_fps or "same"))
        self.parallel_check.setChecked(config.parallel)
        self.workers_spin.setValue(config.workers)
        self.dry_run_check.setChecked(config.dry_run)
        self.collision_combo.setCurrentText(config.collision_policy)
        self.csv_check.setChecked(config.enable_csv_log)
        self.csv_path_edit.setText(config.csv_log_path)
        self.json_check.setChecked(config.enable_json_log)
        self.json_path_edit.setText(config.json_log_path)
        self.theme_combo.setCurrentText(config.theme)
        self.set_output_dir(config.output_dir)
        self.use_gpu_check.setChecked(getattr(config, 'use_gpu', True))
        self.gpu_type_combo.setCurrentText(getattr(config, 'gpu_type', 'none'))
        self.hw_decode_check.setChecked(getattr(config, 'use_hw_decode', True))
        self.copy_audio_check.setChecked(getattr(config, 'copy_audio', False))
        self.skip_reencode_check.setChecked(getattr(config, 'skip_reencode', False))

    def apply_to_config(self, config: AppConfig) -> None:
        config.video_codec = self.codec_combo.currentText()
        config.crf = int(self.crf_spin.value())
        config.preset = self.preset_combo.currentText()
        config.audio_codec = self.audio_combo.currentText()
        config.audio_bitrate_kbps = int(self.audio_bitrate.value())
        fps_text = self.fps_combo.currentText()
        config.target_fps = None if fps_text == "same" else int(fps_text)
        config.parallel = self.parallel_check.isChecked()
        config.workers = int(self.workers_spin.value())
        config.dry_run = self.dry_run_check.isChecked()
        config.collision_policy = self.collision_combo.currentText()
        config.enable_csv_log = self.csv_check.isChecked()
        config.csv_log_path = self.csv_path_edit.text().strip()
        config.enable_json_log = self.json_check.isChecked()
        config.json_log_path = self.json_path_edit.text().strip()
        config.theme = self.theme_combo.currentText()
        config.use_gpu = self.use_gpu_check.isChecked()
        config.gpu_type = self.gpu_type_combo.currentText()
        config.use_hw_decode = self.hw_decode_check.isChecked()
        config.copy_audio = self.copy_audio_check.isChecked()
        config.skip_reencode = self.skip_reencode_check.isChecked()
