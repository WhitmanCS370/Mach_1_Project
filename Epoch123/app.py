from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QThread
import sys
from FileNavigator import FileNavigator
from eutils import get_main_sound_dir_path
import os
import logging
from MetaData import MetaDataDB
from pydub import AudioSegment
from AudioManager import AudioPlayer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123 Audio Viewer")
        self.setMinimumSize(850, 650)
        self.metaDataDB = MetaDataDB()
        self.audio_path = get_main_sound_dir_path('Epoch123/ESMD')
        self.scan_and_insert_metadata(self.audio_path)

        self.audio_player = AudioPlayer()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.file_navigator = FileNavigator(self)
        self.stack.addWidget(self.file_navigator)

    def scan_and_insert_metadata(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.wav', '.flac', '.mp3')):
                    full_path = os.path.join(root, file)
                    try:
                        audio = AudioSegment.from_file(full_path)
                        num_channels = audio.channels
                        sample_rate = audio.frame_rate
                        duration = round(audio.duration_seconds, 2)
                        file_size = round(os.path.getsize(full_path) / 1024, 2)
                        self.metaDataDB.insert_metadata(file, full_path, num_channels, sample_rate, file_size, duration)
                    except Exception as e:
                        logging.error(f"Failed to read or insert metadata for {file}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
