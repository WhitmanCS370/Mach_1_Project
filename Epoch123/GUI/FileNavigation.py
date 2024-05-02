import os
from PySide6.QtWidgets import QFrame, QLabel, QTreeView, QFileSystemModel, QMenu, QMessageBox, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog
from PySide6.QtGui import  QAction 
from PySide6.QtCore import Qt
from WaveformDisplay import WaveformDisplayFN
import e123utils as eutils
import shutil
import tempfile
from Button import Button

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

        # set the background color to #5C3566
        self.setStyleSheet("background-color: #232323")
        
        self.model = CustomFileSystemModel()
        self.model.setReadOnly(False)  # Make the model editable

        # Create the layout
        self.layout = QHBoxLayout()
        # Set the layout to the main window
        self.setLayout(self.layout)
        # self.layout.setSpacing(0)
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # Create two widgets
        self.file_nav_widget = QTreeView()
        # set the background color to #5C3566
        self.file_nav_widget.setStyleSheet("background-color: #151515")
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

            # Welcome widget
        self.welcome_widget = QLabel("Welcome! Select a file to start.")
        self.welcome_widget.setStyleSheet("font-size: 18pt; color: white;")
        self.welcome_widget.setAlignment(Qt.AlignCenter)
        # upload a file
        self.upload_file_button = Button("Upload File", self.upload_file, setFixedWidth=200)
        self.info_layout.addWidget(self.upload_file_button)
        # record a file
        self.record_file_button = Button("Record", self.record_file, setFixedWidth=200)
        self.info_layout.addWidget(self.record_file_button)
        # 
        # add the welcome widget to the info layout
        self.info_layout.addWidget(self.welcome_widget)


        # Connect the signals
        self.file_nav_widget.clicked.connect(self.on_tree_item_clicked)
        self.file_nav_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_nav_widget.customContextMenuRequested.connect(self.show_context_menu)


        self.deleted_files = {}

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Upload File', '', 'Audio Files (*.wav *.mp3)')
        if file_path:
            file_name = os.path.basename(file_path)
            
            # Dialog to ask user to edit or save directly
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Upload Action")
            msg_box.setText("Would you like to edit the file or save it directly?")
            edit_button = msg_box.addButton("Edit", QMessageBox.AcceptRole)
            save_button = msg_box.addButton("Save", QMessageBox.AcceptRole)
            msg_box.addButton("Cancel", QMessageBox.RejectRole)
            msg_box.exec_()
            
            if msg_box.clickedButton() == edit_button:
                # Open file in editor
                self.gui.show_sound_editor()
                self.gui.sound_editor.set_file_to_edit(file_path)
            elif msg_box.clickedButton() == save_button:
                # Save directly
                self.save_uploaded_file(file_path, file_name)


    def save_uploaded_file(self, file_path, file_name):
        # Prompt user to choose directory within ESMD to save the file
        dest_dir = QFileDialog.getExistingDirectory(self, "Select Directory", eutils.get_main_sound_dir_path('Epoch123/ESMD'))
        if dest_dir:
            dest_path = os.path.join(dest_dir, file_name)
            shutil.copy(file_path, dest_path)
            # Update the metadata and refresh view
            self.meta_data.write_metadata(dest_path)
            self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))

    def record_file(self):
        pass

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
        if os.path.isfile(file_path):
            if self.info_layout.count() > 0:
                # Clear the info layout
                for i in reversed(range(self.info_layout.count())): 
                    widget = self.info_layout.itemAt(i).widget()
                    if widget is not None:
                        widget.deleteLater()
            # Add the waveform display widget
            self.info_layout.addWidget(WaveformDisplayFN(self.gui, file_path))
