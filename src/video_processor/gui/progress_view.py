from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from .models import ProgressTableModel, StatusFilterProxy


class ProgressDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        value = index.data(QtCore.Qt.UserRole)
        if value is None:
            super().paint(painter, option, index)
            return
        progress = QtWidgets.QStyleOptionProgressBar()
        progress.rect = option.rect
        progress.minimum = 0
        progress.maximum = 100
        progress.progress = int(value)
        progress.text = f"{value}%"
        progress.textVisible = True
        QtWidgets.QApplication.style().drawControl(
            QtWidgets.QStyle.CE_ProgressBar, progress, painter
        )


class ProgressView(QtWidgets.QWidget):
    startRequested = QtCore.Signal()
    pauseRequested = QtCore.Signal()
    resumeRequested = QtCore.Signal()
    cancelRequested = QtCore.Signal()
    retryRequested = QtCore.Signal()
    openOutputRequested = QtCore.Signal()
    copyLogRequested = QtCore.Signal()
    filterChanged = QtCore.Signal(str)
    infoRequested = QtCore.Signal(object)
    inputChanged = QtCore.Signal()
    outputChanged = QtCore.Signal()
    refreshRequested = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.model = ProgressTableModel([])
        self.in_progress_proxy = StatusFilterProxy()
        self.in_progress_proxy.setSourceModel(self.model)
        self.in_progress_proxy.set_status_whitelist(["queued", "running"])
        self.completed_proxy = StatusFilterProxy()
        self.completed_proxy.setSourceModel(self.model)
        self.completed_proxy.set_status_whitelist(
            ["completed", "failed", "skipped", "canceled"]
        )

        self.input_edit = QtWidgets.QLineEdit()
        self.input_button = QtWidgets.QPushButton("Browse")
        self.output_edit = QtWidgets.QLineEdit()
        self.output_button = QtWidgets.QPushButton("Browse")

        self.input_button.clicked.connect(self._browse_input)
        self.output_button.clicked.connect(self._browse_output)
        self.input_edit.editingFinished.connect(self.inputChanged.emit)
        self.output_edit.editingFinished.connect(self.outputChanged.emit)

        self.summary_label = QtWidgets.QLabel("Ready")
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(["all", "completed", "failed", "skipped", "canceled"])
        self.filter_combo.currentTextChanged.connect(self.filterChanged.emit)
        self.set_completed_filter("all")

        self.start_button = QtWidgets.QPushButton("Start")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.resume_button = QtWidgets.QPushButton("Resume")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.retry_button = QtWidgets.QPushButton("Retry Failed")
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.open_output_button = QtWidgets.QPushButton("Open Output")
        self.copy_log_button = QtWidgets.QPushButton("Copy Log Path")

        self.start_button.clicked.connect(self.startRequested.emit)
        self.pause_button.clicked.connect(self.pauseRequested.emit)
        self.resume_button.clicked.connect(self.resumeRequested.emit)
        self.cancel_button.clicked.connect(self.cancelRequested.emit)
        self.retry_button.clicked.connect(self.retryRequested.emit)
        self.refresh_button.clicked.connect(self.refreshRequested.emit)
        self.open_output_button.clicked.connect(self.openOutputRequested.emit)
        self.copy_log_button.clicked.connect(self.copyLogRequested.emit)

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.resume_button)
        controls_layout.addWidget(self.cancel_button)
        controls_layout.addWidget(self.retry_button)
        controls_layout.addWidget(self.refresh_button)
        controls_layout.addStretch(1)
        controls_layout.addWidget(QtWidgets.QLabel("Filter:"))
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addWidget(self.open_output_button)
        controls_layout.addWidget(self.copy_log_button)

        self.in_progress_table = QtWidgets.QTableView()
        self.in_progress_table.setModel(self.in_progress_proxy)
        self._configure_table(self.in_progress_table)
        self.in_progress_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self.in_progress_table, self.in_progress_proxy, pos)
        )

        self.completed_table = QtWidgets.QTableView()
        self.completed_table.setModel(self.completed_proxy)
        self._configure_table(self.completed_table)
        self.completed_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self.completed_table, self.completed_proxy, pos)
        )

        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.input_button)
        form.addRow("Input folder", input_layout)

        output_layout = QtWidgets.QHBoxLayout()
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(self.output_button)
        form.addRow("Output folder", output_layout)

        layout.addLayout(form)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(controls_layout)

        self.in_progress_group = QtWidgets.QGroupBox("In Progress (0)")
        in_progress_layout = QtWidgets.QVBoxLayout(self.in_progress_group)
        self.in_progress_empty = QtWidgets.QLabel("No items yet.")
        self.in_progress_empty.setAlignment(QtCore.Qt.AlignCenter)
        in_progress_layout.addWidget(self.in_progress_empty)
        in_progress_layout.addWidget(self.in_progress_table)

        self.completed_group = QtWidgets.QGroupBox("Completed (0)")
        self.completed_group.setVisible(False)
        completed_layout = QtWidgets.QVBoxLayout(self.completed_group)
        completed_layout.addWidget(self.completed_table)

        layout.addWidget(self.in_progress_group)
        layout.addWidget(self.completed_group)

    def set_summary(self, text: str) -> None:
        self.summary_label.setText(text)

    def set_overall_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def update_section_titles(
        self, *, in_progress_count: int, completed_count: int
    ) -> None:
        self.in_progress_group.setTitle(f"In Progress ({in_progress_count})")
        self.in_progress_empty.setVisible(in_progress_count == 0)
        self.in_progress_table.setVisible(in_progress_count > 0)
        if completed_count > 0:
            self.completed_group.setTitle(f"Completed ({completed_count})")
            self.completed_group.setVisible(True)
        else:
            self.completed_group.setVisible(False)

    def get_input_dir(self) -> str:
        return self.input_edit.text().strip()

    def get_output_dir(self) -> str:
        return self.output_edit.text().strip()

    def set_input_dir(self, value: str) -> None:
        self.input_edit.setText(value)

    def set_output_dir(self, value: str) -> None:
        self.output_edit.setText(value)

    def _browse_input(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if path:
            self.input_edit.setText(path)
            self.inputChanged.emit()

    def _browse_output(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_edit.setText(path)
            self.outputChanged.emit()

    def _configure_table(self, table: QtWidgets.QTableView) -> None:
        table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        table.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        table.setIconSize(QtCore.QSize(96, 54))
        table.verticalHeader().setDefaultSectionSize(60)
        table.setItemDelegateForColumn(3, ProgressDelegate(table))
        table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def set_completed_filter(self, status: str) -> None:
        if status == "all":
            self.completed_proxy.set_status_whitelist(
                ["completed", "failed", "skipped", "canceled"]
            )
        else:
            self.completed_proxy.set_status_whitelist([status])

    def _show_context_menu(self, table, proxy, pos) -> None:
        index = table.indexAt(pos)
        if not index.isValid():
            return
        source_index = proxy.mapToSource(index)
        item = self.model.get_item(source_index.row())
        if not item:
            return
        menu = QtWidgets.QMenu(self)
        info_action = menu.addAction("Info")
        action = menu.exec(table.viewport().mapToGlobal(pos))
        if action == info_action:
            self.infoRequested.emit(item)
