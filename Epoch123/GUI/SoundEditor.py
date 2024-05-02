from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame, QComboBox, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
from WaveformDisplay import WaveformDisplaySE
from Button import Button
import e123utils as eutils
import os
import shutil


class SoundEditor(QFrame):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.meta_data_obj = self.window.metaData

        self.current_file = None

        layout = QVBoxLayout()

        self.setLayout(layout)

        self.frame_travel_btns = QHBoxLayout()
        self.back_button = Button("\u2190", self.window.show_file_nav)
        self.frame_travel_btns.addWidget(self.back_button)
        # open metadata editor
        self.edit_metadata_button = Button("Edit Metadata")
        self.frame_travel_btns.addWidget(self.edit_metadata_button)
        # save changes
        self.save_button = Button("Save", self.save_changes)
        self.frame_travel_btns.addWidget(self.save_button)
        # 

        self.layout().addLayout(self.frame_travel_btns)

        self.edit_widget = QWidget()
        self.edit_widget.setLayout(QHBoxLayout())
        layout.addWidget(self.edit_widget)

        self.edit_options_widget = QWidget()
        self.edit_options_widget.setLayout(QVBoxLayout())
        self.edit_widget.layout().addWidget(self.edit_options_widget)

        # Crop button
        self.crop_button = Button("Crop")
        self.edit_options_widget.layout().addWidget(self.crop_button)

        # Filters dropdown menu
        self.filters_menu = QComboBox()
        self.filters_menu.addItem("Filter 1")
        self.filters_menu.addItem("Filter 2")
        self.filters_menu.addItem("Filter 3")
        self.filters_menu.addItem("Filter 4")
        self.filters_menu.addItem("Filter 5")
        self.edit_options_widget.layout().addWidget(self.filters_menu)

        # Apply filter button
        self.apply_filter_button = Button("Apply Filter")
        self.edit_options_widget.layout().addWidget(self.apply_filter_button)

        # Frequency dropdown menu

        self.audio = None
        self.audio_player = None

    def save_changes(self):
        # check if the current file already exists in metatagdata.json
        # do this by getting the metadata of the current file
        metadata = self.meta_data_obj.get_file_metadata(self.current_file)
        if not metadata:
            # ask the user if they save just the changes or create a new metadata entry
            # which saves the file to the metadata.json file and the ESMD folder
                        # Dialog to ask user to edit or save directly

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Save Action")
            msg_box.setText("Would you like to save just the changes or create a new metadata entry?")
            save_changes_button = msg_box.addButton("Save Changes", QMessageBox.AcceptRole)
            save_new_button = msg_box.addButton("Save File", QMessageBox.AcceptRole)
            msg_box.addButton("Cancel", QMessageBox.RejectRole)
            msg_box.exec_()
            file_name = os.path.basename(self.current_file)

            if msg_box.clickedButton() == save_changes_button:
                # update the metadata entry
                return
            elif msg_box.clickedButton() == save_new_button:
                dest_dir = QFileDialog.getExistingDirectory(self, "Select Directory", eutils.get_main_sound_dir_path('Epoch123/ESMD'))
                if dest_dir:
                    dest_path = os.path.join(dest_dir, file_name)
                    shutil.copy(self.current_file, dest_path)
                    # Update the metadata and refresh view
                    self.meta_data_obj.write_metadata(dest_path)
                    # self.model.setRootPath(eutils.get_main_sound_dir_path('Epoch123/ESMD'))
                else:
                    # update the metadata entry
                    self.meta_data_obj.write_metadata(self.current_file)


    def set_file_to_edit(self, file_path):
        self.current_file = file_path

        # Check if waveform_display already exists
        if hasattr(self, 'waveform_display'):
            # Remove the existing waveform_display from the layout
            self.edit_widget.layout().removeWidget(self.waveform_display)
            # Delete the existing waveform_display
            self.waveform_display.deleteLater()

        self.waveform_display = WaveformDisplaySE(self.window, self.current_file)
        self.waveform_display.setLayout(QVBoxLayout())
        self.edit_widget.layout().addWidget(self.waveform_display)
