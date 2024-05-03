from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileSystemModel

class CustomFileSystemModel(QFileSystemModel):
    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 1:
            flags &= ~Qt.ItemIsEditable
        return flags