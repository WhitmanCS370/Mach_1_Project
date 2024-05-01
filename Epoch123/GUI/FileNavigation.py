import os
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QTreeView, QFileSystemModel, QMenu, QMessageBox, QAbstractItemView, QVBoxLayout, QSplitter, QWidget, QHBoxLayout
from PySide6.QtGui import  QAction 
from PySide6.QtCore import Qt
from WaveformDisplay import WaveformDisplay
import e123utils as eutils
import shutil
import tempfile

class CustomFileSystemModel(QFileSystemModel):
    def flags(self, index):
        flags = super().flags(index)

        # Make the file extension column non-editable
        if index.column() == 1:
            flags &= ~Qt.ItemIsEditable

        return flags

class FileNavigation(QFrame):
    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui
        self.meta_data = self.gui.metaData
        
        self.model = CustomFileSystemModel()
        self.model.setReadOnly(False)  # Make the model editable

        # Create the layout
        self.layout = QHBoxLayout()
        # self.layout.setSpacing(0)
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # Create two widgets
        self.file_nav_widget = QTreeView()
        self.file_nav_widget.setMinimumWidth(200)
        self.file_nav_widget.setMaximumWidth(200)
        self.file_nav_widget.setModel(self.model)
        self.file_nav_widget.model().setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))
        self.file_nav_widget.setRootIndex(self.file_nav_widget.model().index(eutils.get_main_sound_dir_path('Epoch123/ESMD')))
        self.file_nav_widget.setHeaderHidden(True)
        self.file_nav_widget.setColumnHidden(1, True)
        self.file_nav_widget.setColumnHidden(2, True)
        self.file_nav_widget.setColumnHidden(3, True)

        # Add widgets to the layout
        self.layout.addWidget(self.file_nav_widget)

        self.info_layout = QVBoxLayout()
        self.info_widget = QWidget()
        self.info_widget.setLayout(self.info_layout)
        self.layout.addWidget(self.info_widget)

        # Set the layout to the main window
        self.setLayout(self.layout)

        # Connect the signals
        self.file_nav_widget.clicked.connect(self.on_tree_item_clicked)
        self.file_nav_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_nav_widget.customContextMenuRequested.connect(self.show_context_menu)


        self.deleted_files = {}

    def show_context_menu(self, position):
        index = self.file_nav_widget.indexAt(position)

        context_menu = QMenu(self)

        if index.isValid():  # A tree item is clicked
            rename_action = QAction('Rename', self)
            rename_action.triggered.connect(lambda: self.file_nav_widget.edit(index))  # Start editing manually
            context_menu.addAction(rename_action)

            delete_action = QAction('Delete', self)
            delete_action.triggered.connect(lambda: self.delete_file(self.model.filePath(index)))
            context_menu.addAction(delete_action)

            create_folder_action = QAction('Create Folder', self)
            create_folder_action.triggered.connect(self.create_folder)
            context_menu.addAction(create_folder_action)
        else:  # The background is clicked
            undo_action = QAction('Undo Delete', self)
            undo_action.triggered.connect(self.undo_delete)
            context_menu.addAction(undo_action)

            create_folder_action = QAction('Create Folder', self)
            create_folder_action.triggered.connect(self.create_folder)
            context_menu.addAction(create_folder_action)

        context_menu.exec_(self.file_nav_widget.viewport().mapToGlobal(position))

    def on_file_renamed(self, path, old_name, new_name):
        old_path = os.path.join(path, old_name)
        new_path = os.path.join(path, new_name)

        # Update the metadata
        self.meta_data.rename_file(old_path, new_path)

    def delete_file(self, file_path):
        confirm = QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            temp_dir = tempfile.gettempdir()
            base_name = os.path.basename(file_path)
            temp_file_path = os.path.join(temp_dir, base_name)
            
            # Generate a unique name for the placeholder directory
            counter = 1
            while os.path.exists(temp_file_path):
                temp_file_path = os.path.join(temp_dir, f"{base_name} ({counter})")
                counter += 1

            if os.path.isfile(file_path):
                shutil.move(file_path, temp_file_path)  # Move the file to the temp directory
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the directory and all its contents
                os.mkdir(temp_file_path)  # Create a placeholder in the temp directory

            self.deleted_files[temp_file_path] = file_path  # Store the original file path
            self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))  # refresh the view

            # Update the metadata
            self.meta_data.delete_file(file_path)

    def undo_delete(self):
        if self.deleted_files:
            temp_file_path, original_file_path = self.deleted_files.popitem()
            shutil.move(temp_file_path, original_file_path)  # Move the file back to its original location
            self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))  # refresh the view

            # Update the metadata
            self.meta_data.write_metadata(original_file_path)

    def create_folder(self):
        # Get the currently selected item
        index = self.file_nav_widget.currentIndex()
        if not index.isValid():
            return

        # Determine the parent directory for the new folder
        file_path = self.model.filePath(index)
        if not os.path.isdir(file_path):  # If the selected item is a file, get its parent directory
            file_path = os.path.dirname(file_path)

        # Create a new folder with a default name
        default_folder_name = "New Folder"
        folder_path = os.path.join(file_path, default_folder_name)
        os.mkdir(folder_path)

        # Refresh the view
        self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))

        # Find the new folder in the tree view and start editing
        index = self.model.index(folder_path)
        self.file_nav_widget.setCurrentIndex(index)
        self.file_nav_widget.edit(index)
                
    def on_tree_item_clicked(self, index):
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):  # Check if the clicked item is a file
            if self.info_layout.count() > 0:
                self.info_layout.itemAt(0).widget().deleteLater()
            self.info_layout.addWidget(WaveformDisplay(self.gui, file_path))