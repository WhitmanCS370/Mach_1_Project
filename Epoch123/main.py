import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from FileNavigationWidget import FileNavigationWidget
from AudioManager import AudioManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123 Audio Viewer")
        self.setMinimumSize(850, 650)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.audio_manager = None

        self.file_nav_widget = FileNavigationWidget(self)
        self.central_widget.addWidget(self.file_nav_widget)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
