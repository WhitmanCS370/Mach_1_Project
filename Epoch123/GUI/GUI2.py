from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
import sys
import e123utils as eutils
import os

from FileNavigation import FileNavigation
from MetaDataEditor import MetaDataEditor
from Metadata import MetaData

class GUI2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123")
        self.setMinimumSize(800, 600)

        self.metaData = MetaData()
        self.metaData.set_tags()

        # Create a QStackedWidget and set it as the central widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Add the FileNavigation widget to the QStackedWidget
        self.file_nav = FileNavigation(self)
        # self.file_nav.setFixedWidth(300)
        self.stacked_widget.addWidget(self.file_nav)

        # Add the MetaDataEditor widget to the QStackedWidget
        self.meta_data_editor = MetaDataEditor(self)
        self.stacked_widget.addWidget(self.meta_data_editor)

        self.audio_player = None

    def write_metadata_for_dir(self, dir_path):
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                self.metaData.write_metadata(file_path)

    # Add a method to switch to the FileNavigation widget
    def show_file_nav(self):
        self.stacked_widget.setCurrentIndex(0)

    # Add a method to switch to the MetaDataEditor widget
    def show_meta_data_editor(self):
        self.stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = GUI2()
    window.show()

    # search the ESMD directory for sound files
    ESMD_dir = eutils.get_main_sound_dir_path('Epoch123/ESMD/')
    window.write_metadata_for_dir(ESMD_dir)

    sys.exit(app.exec())