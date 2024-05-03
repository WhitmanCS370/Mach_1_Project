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
from Button import Button
from MetaData import MetaDataWidget

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

class FileNavigationWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #232323")
        self.setLayout(QHBoxLayout())
        self.model = CustomFileSystemModel(parent)
        self.model.setReadOnly(False)
        self.plot_widget = WaveformPlotWidget(parent)
        self.deleted_files = {}
        self.currently_selected_file = None
        self.root_path = eutils.get_main_sound_dir_path('Epoch123/ESMD')
        self.metadata_widget = MetaDataWidget(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        self.file_nav_layout = QVBoxLayout()
        self.layout().addLayout(self.file_nav_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setMinimumWidth(350)
        self.search_bar.setMaximumWidth(400)
        self.search_bar.setStyleSheet("background-color: #151515; color: white; padding: 2px; border: 1px solid #151515; border-radius: 5px; font-size: 14px")
        self.file_nav_layout.addWidget(self.search_bar)

        self.setup_file_tree()

        self.info_widget = QWidget()
        self.info_widget.setLayout(QVBoxLayout())
        self.layout().addWidget(self.info_widget)
        self.file_title = QLabel("No file selected")
        self.file_title.setStyleSheet("color: white; font-size: 20px")
        self.file_title.setAlignment(Qt.AlignCenter)
        self.info_widget.layout().addWidget(self.file_title)
        button_widget = self.plot_widget.audio_buttons()
        self.plot_widget.layout.addWidget(button_widget)
        self.plot_widget.layout.addWidget(self.metadata_widget)
        self.info_widget.layout().addWidget(self.plot_widget)
        self.info_widget.layout().addLayout(self.edit_buttons())
        self.plot_widget.hide()
        self.file_tree.clicked.connect(self.on_file_selected)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)

    def edit_buttons(self):
        edit_buttons_layout = QHBoxLayout()
        edit_buttons_layout.setSpacing(10)
        edit_buttons_layout.setAlignment(Qt.AlignCenter)
        edit_buttons_layout.addWidget(Button("Edit File", None))
        edit_buttons_layout.addWidget(Button("Delete File", None))
        return edit_buttons_layout
    

    def setup_file_tree(self):
        self.file_tree = CustomTreeView()
        self.file_tree.setMinimumWidth(200)
        self.file_tree.setMaximumWidth(400)
        self.file_tree.setModel(self.model)
        self.model.setRootPath(self.root_path)
        self.file_tree.setRootIndex(self.model.index(self.root_path))
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

        if not os.path.isfile(file_path):
            if self.plot_widget.isVisible():
                return
            else:
                self.plot_widget.hide()
                return

        self.file_title.setText(f"Selected File: {self.currently_selected_file}")
        self.metadata_widget.update_metadata(file_path)
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

        # rename_action = self.create_action('Rename', lambda: QTreeView.edit(self.file_tree, index))
        rename_action = self.create_action('Rename', lambda: self.rename_file(index))
        delete_action = self.create_action('Delete', lambda: self.delete_file(self.model.filePath(index)))
        create_folder_action = self.create_action('Create Folder', lambda: self.create_folder(index))
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


    def refresh_view(self):
        self.model.setRootPath(self.root_path)
    
    def delete_file(self, file_path):
        if QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            temp_file_path = self.get_unique_temp_path(os.path.basename(file_path))
            if os.path.isfile(file_path):
                shutil.move(file_path, temp_file_path)
                self.parent.metaDataDB.delete_file(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                os.mkdir(temp_file_path)
            self.deleted_files[temp_file_path] = file_path
            self.refresh_view()

    def undo_delete(self):
        if self.deleted_files:
            temp_file_path, original_file_path = self.deleted_files.popitem()
            shutil.move(temp_file_path, original_file_path)
            self.parent.metaDataDB.insert_metadata(original_file_path)
            self.refresh_view()

    def get_parent_path(self, index):
        if index and index.isValid():
            file_path = self.model.filePath(index)
            if os.path.isfile(file_path):
                return os.path.dirname(file_path)
            else:
                return file_path
        else:
            return self.root_path

    def rename_file(self, index):
        if index and index.isValid():
            file_path = self.model.filePath(index)
            new_name = QTreeView.edit(self.file_tree, index)
            if new_name is None:
                return
            new_path = os.path.join(self.get_parent_path(index), new_name)
            if os.path.isfile(file_path):
                self.parent.metaDataDB.rename_file(file_path, new_path)
            else:
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        self.parent.metaDataDB.rename_file(full_path, new_path)
        self.refresh_view()

    def create_folder(self, index=None):
        parent_path = self.get_parent_path(index)
        default_folder_name = "New Folder"
        folder_path = os.path.join(parent_path, default_folder_name)
        os.mkdir(folder_path)
        self.refresh_view()
        new_index = self.model.index(folder_path)
        self.file_tree.setCurrentIndex(new_index)
        self.file_tree.edit(new_index, QTreeView.EditKeyPressed, None)

    def delete_file(self, file_path):
        if os.path.exists(file_path) and QMessageBox.question(self, 'Delete file', 'Are you sure you want to delete this file?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            temp_file_path = self.get_unique_temp_path(os.path.basename(file_path))
            if os.path.isfile(file_path):
                shutil.move(file_path, temp_file_path)
                self.parent.metaDataDB.delete_file(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                os.mkdir(temp_file_path)
            self.deleted_files[temp_file_path] = file_path
            self.refresh_view()