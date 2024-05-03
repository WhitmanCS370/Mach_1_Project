import os
import soundfile as sf
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QLabel, QFileSystemModel, QTreeView, QHBoxLayout, QMenu, QMessageBox, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from functools import lru_cache
from WaveformPlotWidget import WaveformPlotWidget
import e123utils as eutils
from pydub import AudioSegment
import tempfile
import logging
import shutil


class CustomFileSystemModel(QFileSystemModel):
    def flags(self, index):
        return super().flags(index)

class FileNavigationWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set the background color to #232323
        self.setStyleSheet("background-color: #232323")
        # Set the layout to the Frame
        self.setLayout(QHBoxLayout())
        # Create the model
        self.model = CustomFileSystemModel()
        self.model.setReadOnly(False)
        # Create the plot widget
        self.plot_widget = WaveformPlotWidget(parent)
        # Create a dictionary to store deleted files
        self.deleted_files = {}
        # Set the currently selected file to None
        self.currently_selected_file = None
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        # Set up file navigation layout
        self.file_nav_layout = QVBoxLayout()
        self.layout().addLayout(self.file_nav_layout)

        # Add search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setMinimumWidth(350)
        self.search_bar.setMaximumWidth(400)
        self.search_bar.setStyleSheet("background-color: #151515; color: white; padding: 2px; border: 1px solid #151515; border-radius: 5px")
        self.file_nav_layout.addWidget(self.search_bar)

        # Set up file tree
        self.setup_file_tree()

        # Set up info widget
        self.info_widget = QWidget()
        self.info_widget.setLayout(QVBoxLayout())
        self.layout().addWidget(self.info_widget)
        # Set up file title and plot widget
        self.file_title = QLabel("No file selected")
        self.file_title.setStyleSheet("color: white; font-size: 20px")
        self.file_title.setAlignment(Qt.AlignCenter)
        self.info_widget.layout().addWidget(self.file_title)
        button_widget = self.plot_widget.audio_buttons()
        self.plot_widget.layout.addWidget(button_widget)
        self.info_widget.layout().addWidget(self.plot_widget)
        # hide the plot widget
        self.plot_widget.hide()
        self.file_tree.clicked.connect(self.on_file_selected)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)

    def setup_file_tree(self):
        self.file_tree = QTreeView()
        self.file_tree.setStyleSheet("background-color: #151515")
        self.file_tree.setMinimumWidth(200)
        self.file_tree.setMaximumWidth(400)
        root_path = eutils.get_main_sound_dir_path('Epoch123/ESMD')
        self.file_tree.setModel(self.model)
        self.file_tree.model().setRootPath(root_path)
        self.file_tree.setRootIndex(self.file_tree.model().index(root_path))
        self.file_tree.setHeaderHidden(True)
        for col in range(1, 4):
            self.file_tree.setColumnHidden(col, True)
        self.file_nav_layout.addWidget(self.file_tree)


    @lru_cache(maxsize=50)
    def load_audio(self, file_path):
        try:
            data, fs = sf.read(file_path)
            return data[:, 0] if data.ndim > 1 else data, fs
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading audio: {e}")
            raise RuntimeError(f"Error loading audio: {e}")
        
    @lru_cache(maxsize=50)
    def get_unique_temp_path(self, base_name):
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, base_name)
        counter = 1
        while os.path.exists(temp_file_path):
            temp_file_path = os.path.join(temp_dir, f"{base_name} ({counter})")
            counter += 1
        return temp_file_path

    def on_file_selected(self, index):
        file_path = self.model.filePath(index)
        self.currently_selected_file = os.path.basename(file_path)

        # Check if the selected item is a file
        if not os.path.isfile(file_path):
            if self.plot_widget.isVisible():
                return
            else:
                self.plot_widget.hide()
                return

        self.file_title.setText(f"Selected File: {self.currently_selected_file}")
        self.plot_widget.show()

        try:
            if file_path not in self.plot_widget.audio_cache:
                data, fs = self.load_audio(file_path)
                audio = AudioSegment.from_file(file_path)
                self.plot_widget.audio_cache[file_path] = (data, fs, audio)

            data, fs, audio = self.plot_widget.audio_cache[file_path]
            self.plot_widget.clear_selection()
            self.plot_widget.update_plot(data, fs, audio)
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", f"Error loading file '{file_path}': {e}")
            logging.error(f"Error loading file '{file_path}': {e}")


    def show_context_menu(self, position):
        index = self.file_tree.indexAt(position)
        context_menu = QMenu(self)

        rename_action = self.create_action('Rename', lambda: self.file_tree.edit(index))
        delete_action = self.create_action('Delete', lambda: self.delete_file(self.model.filePath(index)))
        create_folder_action = self.create_action('Create Folder', self.create_folder)
        undo_action = self.create_action('Undo Delete', self.undo_delete)
        if index.isValid():
            context_menu.addAction(rename_action)
            context_menu.addAction(delete_action)
            context_menu.addAction(create_folder_action)
        else:
            context_menu.addAction(undo_action)
            context_menu.addAction(create_folder_action)

        context_menu.exec_(self.file_tree.viewport().mapToGlobal(position))

    def create_action(self, name, func):
        action = QAction(name, self)
        action.triggered.connect(func)
        return action
    
    def rename(self, index, new_name):
        old_path = self.model.filePath(index)
        old_extension = os.path.splitext(old_path)[1]  # Get the old file's extension

        # Check if the selected item is a file and if the new name has an extension
        if os.path.isfile(old_path) and not os.path.splitext(new_name)[1]:
            new_name += old_extension  # Append the old extension if the new name doesn't have one

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        try:
            os.rename(old_path, new_path)
        except Exception as e:
            logging.error(f"Failed to rename '{old_path}' to '{new_name}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to rename '{old_path}' to '{new_name}': {e}")
            return False
        return True

    def delete_file(self, file_path):
        if QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            temp_file_path = self.get_unique_temp_path(os.path.basename(file_path))
            if os.path.isfile(file_path):
                shutil.move(file_path, temp_file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                os.mkdir(temp_file_path)

            self.deleted_files[temp_file_path] = file_path
            self.refresh_view()

    def undo_delete(self):
        if self.deleted_files:
            temp_file_path, original_file_path = self.deleted_files.popitem()
            shutil.move(temp_file_path, original_file_path)
            self.refresh_view()

    def refresh_view(self):
        self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))

    def create_folder(self):
        # Get the currently selected item
        index = self.file_tree.currentIndex()
        if not index.isValid():
            return

        # Determine the parent directory for the new folder
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):  # If the selected item is a file, get its parent directory
            file_path = os.path.dirname(file_path)

        # Create a new folder with a default name
        default_folder_name = "New Folder"
        folder_path = os.path.join(file_path, default_folder_name)
        os.mkdir(folder_path)

        # Refresh the view
        self.refresh_view()

        # Find the new folder in the tree view and start editing
        index = self.model.index(folder_path)
        self.file_tree.setCurrentIndex(index)
        self.file_tree.edit(index)
