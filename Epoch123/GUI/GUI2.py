from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
import sys
import e123utils as eutils
import os

from FileNavigation import FileNavigation
from Metadata import MetaData

class GUI2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123")
        self.setMinimumSize(800, 600)

        self.metaData = MetaData()
        self.metaData.set_tags()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.file_nav = FileNavigation(self, self.metaData)
        self.file_nav.setFixedWidth(300)
        self.layout.addWidget(self.file_nav)

        self.info_panel = QWidget()
        self.info_layout = QVBoxLayout()
        self.info_panel.setLayout(self.info_layout)
        self.layout.addWidget(self.info_panel)

        self.audio_player = None


    def write_metadata_for_dir(self, dir_path):
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                self.metaData.write_metadata(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = GUI2()
    window.show()

    # search the ESMD directory for sound files
    ESMD_dir = eutils.get_main_sound_dir_path('Epoch123/ESMD/')
    window.write_metadata_for_dir(ESMD_dir)

    sys.exit(app.exec())