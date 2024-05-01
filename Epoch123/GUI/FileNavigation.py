import os
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QTreeView, QFileSystemModel, QMenu, QMessageBox, QAbstractItemView
from PySide6.QtGui import  QAction 
from PySide6.QtCore import Qt
from WaveformDisplay import WaveformDisplay
import e123utils as eutils

class CustomFileSystemModel(QFileSystemModel):
    def flags(self, index):
        flags = super().flags(index)

        # Make the file extension column non-editable
        if index.column() == 1:
            flags &= ~Qt.ItemIsEditable

        return flags

class FileNavigation(QFrame):
    def __init__(self, gui, meta_data):
        super().__init__(gui)
        self.gui = gui
        self.meta_data = meta_data
        self.setLayout(QGridLayout())
        self.layout().addWidget(QLabel("File Navigator"), 0, 0)
        self.tree = QTreeView()
        self.model = CustomFileSystemModel()
        self.model.setReadOnly(False)  # Make the model editable

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Disable default editing
        self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))
        self.tree.setRootIndex(self.model.index(eutils.get_main_sound_dir_path('Epoch123/ESMD')))
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.layout().addWidget(self.tree, 1, 0)

        self.tree.clicked.connect(self.on_tree_item_clicked)
        self.model.fileRenamed.connect(self.on_file_renamed)

    def contextMenuEvent(self, event):
        index = self.tree.indexAt(self.tree.viewport().mapFromGlobal(event.globalPos()))
        if not index.isValid():
            return

        context_menu = QMenu(self)

        rename_action = QAction('Rename', self)
        rename_action.triggered.connect(lambda: self.tree.edit(index))  # Start editing manually
        context_menu.addAction(rename_action)

        delete_action = QAction('Delete', self)
        delete_action.triggered.connect(lambda: self.delete_file(self.model.filePath(index)))
        context_menu.addAction(delete_action)

        context_menu.exec_(event.globalPos())

    def on_file_renamed(self, path, old_name, new_name):
        old_path = os.path.join(path, old_name)
        new_path = os.path.join(path, new_name)

        # Update the metadata
        self.meta_data.rename_file(old_path, new_path)

    def delete_file(self, file_path):
        confirm = QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            os.remove(file_path)
            self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))  # refresh the view

            # Update the metadata
            self.meta_data.delete_file(file_path)
            
    def on_tree_item_clicked(self, index):
        file_path = self.model.filePath(index)
        if self.gui.info_layout.count() > 0:
            self.gui.info_layout.itemAt(0).widget().deleteLater()
        self.gui.info_layout.addWidget(WaveformDisplay(self.gui, file_path, self.meta_data))