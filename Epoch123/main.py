import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from FileNavigationFrame import FileNavigationFrame
from SoundEditorFrame import SoundEditorFrame
from MetaData import MetaDataDB
import e123utils as eutils
import os
import logging
from pydub import AudioSegment

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123 Audio Viewer")
        self.setMinimumSize(850, 650)

        self.metaDataDB = MetaDataDB()

        self.audio_path = eutils.get_main_sound_dir_path('Epoch123/ESMD')

        self.scan_and_insert_metadata(self.audio_path)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.audio_manager = None

        self.file_nav_widget = FileNavigationFrame(self)
        self.central_widget.addWidget(self.file_nav_widget)
        self.sound_editor_widget = SoundEditorFrame(self)
        self.central_widget.addWidget(self.sound_editor_widget)

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

    def closeEvent(self, event):
        if self.audio_manager:
            self.audio_manager.stop()
        event.accept()

    def show_file_nav_widget(self):
        self.central_widget.setCurrentIndex(0)

    def show_sound_editor_widget(self):
        self.central_widget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    # Create a dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
