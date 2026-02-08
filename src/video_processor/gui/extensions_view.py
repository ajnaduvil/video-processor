from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ..config import default_extensions


class ExtensionsView(QtWidgets.QWidget):
    extensionsChanged = QtCore.Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.checkboxes = {}

        layout = QtWidgets.QVBoxLayout(self)
        button_layout = QtWidgets.QHBoxLayout()
        self.select_all_button = QtWidgets.QPushButton("Select All")
        self.clear_all_button = QtWidgets.QPushButton("Clear All")
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.clear_all_button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        grid = QtWidgets.QGridLayout()
        extensions = default_extensions()
        for idx, ext in enumerate(extensions):
            checkbox = QtWidgets.QCheckBox(ext)
            checkbox.setChecked(True)
            checkbox.toggled.connect(self.extensionsChanged.emit)
            self.checkboxes[ext] = checkbox
            row = idx // 4
            col = idx % 4
            grid.addWidget(checkbox, row, col)
        layout.addLayout(grid)
        layout.addStretch(1)

        self.select_all_button.clicked.connect(self.select_all)
        self.clear_all_button.clicked.connect(self.clear_all)

    def select_all(self) -> None:
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
        self.extensionsChanged.emit()

    def clear_all(self) -> None:
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
        self.extensionsChanged.emit()

    def get_extensions(self) -> list[str]:
        return [ext for ext, cb in self.checkboxes.items() if cb.isChecked()]

    def set_extensions(self, extensions: list[str]) -> None:
        for ext, cb in self.checkboxes.items():
            cb.setChecked(ext in extensions)
        self.extensionsChanged.emit()
