import os
import logging
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

import soundfile as sf
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QLabel, QFileSystemModel, QTreeView, QHBoxLayout, QMenu, QMessageBox, QWidget

from pydub import AudioSegment
from eutils import get_main_sound_dir_path
from PlotWidget import PlotWidget
from AudioManager import AudioWorker
from GUIElements import Button

class CustomFileSystemModel(QFileSystemModel):
    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 1:
            flags &= ~Qt.ItemIsEditable
        return flags

class CustomTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTreeView {
                background-color: #151515; 
                color: white;
                font-size: 14px;  /* Increase font size if needed */
            }
            QTreeView::item {
                height: 25px;  /* Increase the height of each row */
                padding: 4px;  /* Padding inside each item */
            }
            QTreeView::item:selected {
                background-color: #574B90;  /* Background color for selected item */
            }
        """)

    def edit(self, index, trigger, event):
        if not index.isValid():
            return False
        editor = super().edit(index, trigger, event)
        if editor:
            # Customize the QLineEdit used for editing
            line_edit = self.findChild(QLineEdit)
            if line_edit:
                line_edit.setStyleSheet("QLineEdit { border: 2px solid orange; padding: 4px; }")
        return editor

class FileNavigator(QFrame):
    MAX_WIDTH = 500
    MIN_WIDTH = 300
    SEARCH_STYLESHEET = "background-color: #151515; color: white; padding: 2px; border: 1px solid #151515; border-radius: 5px; font-size: 14px"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #232323")
        self.setLayout(QHBoxLayout())
        self.model = CustomFileSystemModel(self)
        self.model.setReadOnly(False)
        self.plot_widget = PlotWidget(self)
        self.deleted_files = {}
        self.currently_selected_file = None
        self.root_path = get_main_sound_dir_path('Epoch123/ESMD')
        self.audio_workers = {}
        self.audio_cache = {}
        self.setup_ui()

    def setup_ui(self):
        self.file_nav_layout = QVBoxLayout()
        self.layout().addLayout(self.file_nav_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setMinimumWidth(self.MIN_WIDTH)
        self.search_bar.setMaximumWidth(self.MAX_WIDTH)
        self.search_bar.setStyleSheet(self.SEARCH_STYLESHEET)
        self.file_nav_layout.addWidget(self.search_bar)

        self.setup_file_tree()
        self.info_widget = self.setup_info_widget()

    def setup_file_tree(self):
        self.file_tree = CustomTreeView()
        self.file_tree.setMinimumWidth(self.MIN_WIDTH)
        self.file_tree.setMaximumWidth(self.MAX_WIDTH)
        self.file_tree.setBaseSize(self.MIN_WIDTH, 0)
        self.file_tree.setModel(self.model)
        self.model.setRootPath(self.root_path)
        self.file_tree.setRootIndex(self.model.index(self.root_path))
        self.file_tree.setHeaderHidden(True)
        for col in range(1, 4):
            self.file_tree.setColumnHidden(col, True)
        self.file_nav_layout.addWidget(self.file_tree)

    def setup_info_widget(self):
        info_widget = QWidget()
        info_widget.setLayout(QVBoxLayout())
        self.layout().addWidget(info_widget)
        self.file_title = QLabel("No file selected")
        self.file_title.setStyleSheet("color: white; font-size: 20px")
        self.file_title.setAlignment(Qt.AlignCenter)
        info_widget.layout().addWidget(self.file_title)
        info_widget.layout().addWidget(self.plot_widget)
        info_widget.layout().addLayout(self.edit_buttons())
        self.plot_widget.hide()
        self.file_tree.clicked.connect(self.on_file_selected)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        return info_widget

    @lru_cache(maxsize=50)
    def load_audio(self, file_path):
        self.current_audio_path = file_path
        data, fs = sf.read(file_path)
        return data[:, 0] if data.ndim > 1 else data, fs

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def on_file_selected(self, index):
        file_path = self.model.filePath(index)
        if Path(file_path).is_dir():
            # If it's a directory, expand or collapse it.
            if self.file_tree.isExpanded(index):
                self.file_tree.collapse(index)
            else:
                self.file_tree.expand(index)
            return  # Do not update info layout when a folder is clicked.
        
        self.currently_selected_file = Path(file_path).name
        if not Path(file_path).is_file():
            if self.plot_widget.isVisible():
                self.plot_widget.hide()
            return

        self.file_title.setText(f"Selected File: {self.currently_selected_file}")
        self.plot_widget.show()

        try:
            if file_path not in self.audio_cache:
                data, fs = self.load_audio(file_path)
                audio = AudioSegment.from_file(file_path)
                self.audio_cache[file_path] = (data, fs, audio)

            data, fs, audio = self.audio_cache[file_path]
            self.plot_widget.clear_selection()
            self.plot_widget.update_plot(data, fs, audio)
        except Exception as e:
            message = f"Error loading file '{file_path}': {e}"
            self.show_error_message(message)
            logging.error(message)


    def show_context_menu(self, position):
        index = self.file_tree.indexAt(position)
        context_menu = QMenu(self)

        if index.isValid():
            context_menu.addAction(self.create_action('Rename', lambda: self.rename_file(index)))
            context_menu.addAction(self.create_action('Delete', lambda: self.delete_file(self.model.filePath(index))))
            context_menu.addAction(self.create_action('Create Folder', lambda: self.create_folder(index)))
        else:
            context_menu.addAction(self.create_action('Undo Delete', self.undo_delete))
            context_menu.addAction(self.create_action('Create Folder', self.create_folder))

        context_menu.exec_(self.file_tree.viewport().mapToGlobal(position))

    def create_action(self, name, func):
        action = QAction(name, self)
        action.triggered.connect(func)
        return action

    def refresh_view(self):
        self.model.setRootPath(self.root_path)

    def get_unique_temp_path(self, base_name):
        """Generate a unique temporary file path."""
        temp_dir = Path(tempfile.gettempdir())
        temp_file_path = temp_dir / base_name
        counter = 1

        # If the file already exists, add a counter suffix to the name
        while temp_file_path.exists():
            temp_file_path = temp_dir / f"{base_name} ({counter})"
            counter += 1

        return str(temp_file_path)

    def delete_file(self, file_path):
        """Move the file to a temporary path for 'deletion'."""
        if Path(file_path).exists() and QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            temp_file_path = self.get_unique_temp_path(Path(file_path).name)
            if Path(file_path).is_file():
                shutil.move(file_path, temp_file_path)
            elif Path(file_path).is_dir():
                shutil.rmtree(file_path)
                os.mkdir(temp_file_path)
            self.deleted_files[temp_file_path] = file_path
            self.refresh_view()

    def undo_delete(self):
        if self.deleted_files:
            temp_file_path, original_file_path = self.deleted_files.popitem()
            shutil.move(temp_file_path, original_file_path)
            self.refresh_view()

    def get_parent_path(self, index):
        if index and index.isValid():
            file_path = Path(self.model.filePath(index))
            return str(file_path.parent) if file_path.is_file() else str(file_path)
        return self.root_path

    def rename_file(self, index):
        if index and index.isValid():
            file_path = Path(self.model.filePath(index))
            new_name = self.file_tree.edit(index, QTreeView.EditKeyPressed, None)
            if new_name:
                new_path = file_path.parent / new_name
                if file_path.is_file():
                    shutil.move(file_path, new_path)
                else:
                    for root, dirs, files in os.walk(str(file_path)):
                        for file in files:
                            shutil.move(Path(root) / file, new_path)
        self.refresh_view()

    def create_folder(self, index=None):
        parent_path = Path(self.get_parent_path(index))
        folder_path = parent_path / "New Folder"
        folder_path.mkdir()
        self.refresh_view()
        new_index = self.model.index(str(folder_path))
        self.file_tree.setCurrentIndex(new_index)
        self.file_tree.edit(new_index, QTreeView.EditKeyPressed, None)

    def edit_buttons(self):
        edit_buttons_layout = QHBoxLayout()
        edit_buttons_layout.setSpacing(10)
        edit_buttons_layout.setAlignment(Qt.AlignCenter)
        edit_buttons_layout.addWidget(Button("Edit File", self.go_to_sound_editor))
        edit_buttons_layout.addWidget(Button("Delete File", lambda: self.delete_file(self.model.filePath(self.file_tree.currentIndex()))))
        return edit_buttons_layout

    def go_to_sound_editor(self):
        if not self.currently_selected_file:
            QMessageBox.warning(self, "No file selected", "Please select a file to edit")
            return
        try:
            data, fs, audio = self.audio_cache[self.model.filePath(self.file_tree.currentIndex())]
            self.plot_widget.clear_selection()
            self.plot_widget.update_plot(data, fs, audio)
        except Exception as e:
            message = f"Error loading file '{self.model.filePath(self.file_tree.currentIndex())}': {e}"
            self.show_error_message(message)
            logging.error(message)
