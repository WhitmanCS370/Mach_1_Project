import os
import logging
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QLabel, QFileSystemModel, QTreeView, QHBoxLayout, QMenu, QMessageBox, QWidget
from PySide6.QtGui import QAction
from eutils import get_main_sound_dir_path
from PlotWidget import PlotWidget
from AudioManager import AudioProcessor, AudioControlWidget
from MetaData import MetaDataWidget
from GUIElements import Button
from eutils import show_error_message

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
                font-size: 14px;
            }
            QTreeView::item {
                height: 25px;
                padding: 4px;
            }
            QTreeView::item:selected {
                background-color: #574B90;
            }
        """)

    def edit(self, index, trigger, event):
        if not index.isValid():
            return False
        editor = super().edit(index, trigger, event)
        if editor:
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
        self.parent = parent
        self.setStyleSheet("background-color: #111111")
        self.setLayout(QHBoxLayout())
        self.model = CustomFileSystemModel(self)
        self.model.setReadOnly(False)
        self.deleted_files = {}
        self.currently_selected_file = None
        self.root_path = get_main_sound_dir_path('Epoch123/ESMD')
        self.audio_workers = {}
        self.audio_cache = {}
        self.plot_widget = PlotWidget(audio_player=self.parent.audio_player)
        # audio_callbacks = [self.plot_widget.play_audio, self.plot_widget.stop_audio, self.plot_widget.pause_audio, self.plot_widget.resume_audio]
        self.audio_controls_widget = AudioControlWidget(audio_player=self.parent.audio_player)
        self.metadata_widget = MetaDataWidget(self.parent)
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
        info_widget.layout().addWidget(self.audio_controls_widget)
        info_widget.layout().addWidget(self.metadata_widget)
        info_widget.layout().addLayout(self.edit_buttons())
        self.plot_widget.hide()
        self.audio_controls_widget.hide()
        self.metadata_widget.hide()
        self.file_tree.clicked.connect(self.on_file_selected)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        return info_widget
    
    def edit_buttons(self):
        edit_buttons_layout = QHBoxLayout()
        edit_buttons_layout.setSpacing(10)
        edit_buttons_layout.setAlignment(Qt.AlignCenter)
        edit_buttons_layout.addWidget(Button("Edit File", self.go_to_sound_editor))
        edit_buttons_layout.addWidget(Button("Delete File", lambda: self.delete_file(self.model.filePath(self.file_tree.currentIndex()))))
        return edit_buttons_layout

    @lru_cache(maxsize=50)
    def load_audio(self, file_path):
        """ Updated to use the new audio processing logic. """
        self.current_audio_path = file_path
        # Assume AudioProcessor is a part of a separate module or defined elsewhere
        processor = AudioProcessor(file_path)
        processor.data_loaded.connect(lambda data, fs, audio_segment: self.handle_data_loaded(data, fs, audio_segment, file_path))
        processor.error_occurred.connect(show_error_message)
        processor.process_audio()
        return None  # Placeholder, actual data handled asynchronously
    
    def handle_data_loaded(self, data, fs, audio_segment, file_path):
        """Handle the data loaded signal from AudioProcessor."""
        if file_path not in self.audio_cache:
            self.audio_cache[file_path] = (data, fs, audio_segment)
        
        fs = int(fs)  # Ensure fs is an integer
        self.parent.audio_player.set_audio(audio_segment, data, fs, file_path)
        self.plot_widget.update_plot(data, fs, audio_segment)
        self.metadata_widget.update_metadata(file_path)
        self.plot_widget.show()
        self.metadata_widget.show()
        # logging.info(f"Data loaded for {file_path}")
        
    def update_widgets(self, file_path, data=None, fs=None, audio=None):
        """Update the plot and metadata widgets with the given data."""
        self.plot_widget.update_plot(data, fs, audio)
        self.metadata_widget.update_metadata(file_path)
        self.plot_widget.show()
        self.metadata_widget.show()

    def on_file_selected(self, index):
        file_path = self.model.filePath(index)
        if Path(file_path).is_dir():
            if self.file_tree.isExpanded(index):
                self.file_tree.collapse(index)
            else:
                self.file_tree.expand(index)
            return

        # Stop the current playing audio if any
        self.audio_controls_widget.audio_player.stop()

        self.currently_selected_file = Path(file_path).name
        if not Path(file_path).is_file():
            self.plot_widget.hide()
            self.audio_controls_widget.hide()
            self.metadata_widget.hide()
            return

        self.file_title.setText(f"Selected File: {self.currently_selected_file}")
        self.plot_widget.show()
        self.audio_controls_widget.show()
        self.metadata_widget.show()

        try:
            if file_path not in self.audio_cache:
                self.load_audio(file_path)  # This is asynchronous
            else:
                data, fs, audio = self.audio_cache[file_path]
                fs = int(fs)  # Ensure fs is an integer
                self.parent.audio_player.set_audio(audio, data, fs, file_path)
                self.update_widgets(file_path, data, fs, audio)

        except Exception as e:
            message = f"Error loading file '{file_path}': {e}"
            show_error_message(message)
            logging.error(message)

    def create_action(self, name, func):
        action = QAction(name, self)
        action.triggered.connect(func)
        return action

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

    def refresh_view(self):
        self.model.setRootPath(self.root_path)

    def get_unique_temp_path(self, base_name):
        """Generate a unique temporary file path."""
        temp_dir = Path(tempfile.gettempdir())
        temp_file_path = temp_dir / base_name
        counter = 1

        while temp_file_path.exists():
            temp_file_path = temp_dir / f"{base_name} ({counter})"
            counter += 1

        return str(temp_file_path)

    def delete_file(self, file_path):
        """Move the file or directory to a temporary path for 'deletion'."""
        if Path(file_path).exists() and QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            temp_file_path = self.get_unique_temp_path(Path(file_path).name)
            if Path(file_path).is_file():
                shutil.move(file_path, temp_file_path)
                self.audio_cache.pop(file_path, None)
                self.audio_workers.pop(file_path, None)
                self.parent.metaDataDB.delete_file(file_path)
            elif Path(file_path).is_dir():
                for root, _, files in os.walk(file_path):
                    for file in files:
                        abs_file_path = Path(root) / file
                        self.audio_cache.pop(str(abs_file_path), None)
                        self.audio_workers.pop(str(abs_file_path), None)
                        self.parent.metaDataDB.delete_file(str(abs_file_path))
                shutil.move(file_path, temp_file_path)
            self.deleted_files[temp_file_path] = file_path
            self.refresh_view()

    def undo_delete(self):
        if self.deleted_files:
            temp_file_path, original_file_path = self.deleted_files.popitem()
            shutil.move(temp_file_path, original_file_path)
            self.refresh_view()

    def rename_file(self, index):
        # if index and index.isValid():
        #     old_path = Path(self.model.filePath(index))
        #     self.file_tree.edit(index, QTreeView.EditKeyPressed, None)
        #     new_name = self.model.data(index, Qt.DisplayRole)
        #     if new_name:
        #         new_path = old_path.parent / new_name
        #         shutil.move(old_path, new_path)

        #         if old_path.is_file():
        #             self.parent.metaDataDB.rename_file(str(old_path), str(new_path))
        #         else:
        #             for root, _, files in os.walk(str(new_path)):
        #                 for file in files:
        #                     original_file_path = Path(root) / file
        #                     relative_path = original_file_path.relative_to(new_path)
        #                     new_file_path = new_path / relative_path
        #                     self.parent.metaDataDB.rename_file(str(original_file_path), str(new_file_path))
        # self.refresh_view()
        pass

    def create_folder(self, index=None):
        parent_path = Path(self.get_parent_path(index))
        folder_path = parent_path / "New Folder"
        folder_path.mkdir()
        self.refresh_view()
        new_index = self.model.index(str(folder_path))
        self.file_tree.setCurrentIndex(new_index)
        self.file_tree.edit(new_index, QTreeView.EditKeyPressed, None)

    def get_parent_path(self, index):
        if index and index.isValid():
            file_path = Path(self.model.filePath(index))
            return str(file_path.parent) if file_path.is_file() else str(file_path)
        return self.root_path

    def go_to_sound_editor(self):
        # if no file is selected, do nothing
        if self.currently_selected_file is None:
            QMessageBox.warning(self, "No file selected", "Please select a file to edit")
            return
        try:
            data, fs, audio = self.audio_cache[self.current_audio_path]
            self.parent.show_sound_editor()
            self.plot_widget.clear_selection()
            self.parent.audio_player.stop()
            fs = int(fs)  # Ensure fs is an integer
            # self.parent.audio_player.set_audio_data(data, fs)
            self.parent.sound_editor.plot_widget.data = data
            self.parent.sound_editor.plot_widget.clear_selection()
            self.parent.sound_editor.plot_widget.update_plot(data, fs, audio)
            self.parent.sound_editor.set_audio_data(data, self.current_audio_path, fs, audio)
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", f"Error loading file '{self.model.filePath(self.file_tree.currentIndex())}': {e}")
            logging.error(f"Error loading file '{self.model.filePath(self.file_tree.currentIndex())}': {e}")

