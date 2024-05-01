from PySide6.QtWidgets import QFrame, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
import os
import json
import yaml
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from Metadata import MetaData

class MetaDataEditor(QFrame):
    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui
        self.meta_data_obj = self.gui.metaData
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.metadata_table = QTableWidget()
        self.metadata_table.setRowCount(3)
        self.metadata_table.setColumnCount(2)
        self.metadata_table.setHorizontalHeaderLabels(["Key", "Value"])
        layout.addWidget(self.metadata_table)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_metadata)
        layout.addWidget(self.save_button)

        # go back to the FileNavigation widget
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.gui.show_file_nav)
        layout.addWidget(self.back_button)

    def save_metadata(self):
        for row in range(self.metadata_table.rowCount()):
            key_item = self.metadata_table.item(row, 0)
            value_item = self.metadata_table.item(row, 1)
            if key_item and value_item:
                key = key_item.text()
                value = value_item.text()
                self.meta_data_obj.set_metadata(key, value)