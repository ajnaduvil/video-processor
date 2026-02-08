from __future__ import annotations

import time
from pathlib import Path
from PySide6 import QtCore, QtGui


class ProgressTableModel(QtCore.QAbstractTableModel):
    headers = [
        "Thumb",
        "File",
        "Status",
        "Progress",
        "Input (MB)",
        "Output (MB)",
        "Elapsed (s)",
        "Message",
    ]

    def __init__(self, items=None) -> None:
        super().__init__()
        self._items = items or []
        self._index = {item.id: idx for idx, item in enumerate(self._items)}
        self._icon_cache = {}

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(self._items)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self._items[index.row()]
        if role == QtCore.Qt.DecorationRole and index.column() == 0:
            if not item.thumbnail_path:
                return None
            icon = self._icon_cache.get(item.thumbnail_path)
            if icon is None:
                path = Path(item.thumbnail_path)
                if path.exists():
                    pix = QtGui.QPixmap(str(path))
                    if not pix.isNull():
                        icon = QtGui.QIcon(pix)
                        self._icon_cache[item.thumbnail_path] = icon
            return icon
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return ""
            if index.column() == 1:
                return item.input_path
            if index.column() == 2:
                return item.status
            if index.column() == 3:
                if item.progress is None:
                    return "..."
                return f"{item.progress}%"
            if index.column() == 4:
                if item.input_bytes:
                    return f"{item.input_bytes / (1024 * 1024):.2f}"
                return ""
            if index.column() == 5:
                if item.output_bytes:
                    output_mb = item.output_bytes / (1024 * 1024)
                    if item.input_bytes and item.status == "completed":
                        saved_percent = (1 - (item.output_bytes / item.input_bytes)) * 100.0
                        return f"{output_mb:.2f} ({saved_percent:.1f}% saved)"
                    return f"{output_mb:.2f}"
                return ""
            if index.column() == 6:
                if item.start_time and item.end_time:
                    return _format_elapsed(item.end_time - item.start_time)
                if item.start_time:
                    return _format_elapsed(time.time() - item.start_time)
                return ""
            if index.column() == 7:
                return item.message or item.error
        if role == QtCore.Qt.UserRole and index.column() == 3:
            return item.progress
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.headers[section]
        return None

    def set_items(self, items) -> None:
        self.beginResetModel()
        self._items = items
        self._index = {item.id: idx for idx, item in enumerate(self._items)}
        self.endResetModel()

    def update_item(self, item) -> None:
        row = self._index.get(item.id)
        if row is None:
            self.beginInsertRows(QtCore.QModelIndex(), len(self._items), len(self._items))
            self._items.append(item)
            self._index[item.id] = len(self._items) - 1
            self.endInsertRows()
            return
        self._items[row] = item
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(
            top_left,
            bottom_right,
            [QtCore.Qt.DisplayRole, QtCore.Qt.DecorationRole],
        )

    def get_item(self, row: int):
        if row < 0 or row >= len(self._items):
            return None
        return self._items[row]


def _format_elapsed(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    total = int(seconds)
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


class StatusFilterProxy(QtCore.QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self.status_filter = "all"
        self.status_whitelist: set[str] | None = None

    def set_status_filter(self, status: str) -> None:
        self.status_filter = status
        self.invalidateFilter()

    def set_status_whitelist(self, statuses: list[str]) -> None:
        self.status_whitelist = set(statuses)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        model = self.sourceModel()
        index = model.index(source_row, 2, source_parent)
        status = model.data(index, QtCore.Qt.DisplayRole)
        if self.status_whitelist is not None:
            return status in self.status_whitelist
        if self.status_filter == "all":
            return True
        return status == self.status_filter
