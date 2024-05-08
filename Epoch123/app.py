from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QThread
import numpy as np
import sys
from AudioManager import AudioPlayer
from FileNavigator import FileNavigator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123 Audio Viewer")
        self.setMinimumSize(850, 650)
        self.current_audio_path = None

        # Initialize AudioPlayer with placeholder values
        self.player = AudioPlayer('', 44100, np.array([]))

        # Create stack of widgets
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create and manage file navigator with audio workers
        self.file_navigator = FileNavigator()
        self.stack.addWidget(self.file_navigator)

        # Initialize audio workers dictionary if not initialized in FileNavigator
        self.audio_workers = getattr(self.file_navigator, 'audio_workers', {})

    def closeEvent(self, event):
        """Cleanup threads before closing."""
        try:
            for thread, worker in list(self.audio_workers.values()):  # Convert to list if you are modifying the dictionary
                if isinstance(thread, QThread) and thread.isRunning():
                    thread.quit()
                    thread.wait()
        except Exception as e:
            print(f"Failed to close threads properly: {e}")
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
