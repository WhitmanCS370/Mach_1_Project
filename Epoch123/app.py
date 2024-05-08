from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QFrame, QHBoxLayout, QMessageBox
from PySide6.QtCore import QThread
from PlotWidget import PlotWidget, AudioWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Epoch123 Audio Viewer")
        self.setMinimumSize(850, 650)

        # Setup GUI components
        self.stack_widget = QStackedWidget(self)
        self.setCentralWidget(self.stack_widget)
        plot_frame = QFrame(self)
        plot_frame.setLayout(QHBoxLayout())
        self.stack_widget.addWidget(plot_frame)

        # Initialize the plot widget and add it to the layout
        self.plot_widget = PlotWidget()
        plot_frame.layout().addWidget(self.plot_widget)

        # Thread and worker setup
        audio_path = "/Users/uliraudales/Desktop/School/SoftwareDesign/Mach_1_Project/Epoch123/ESMD/bird.wav"
        self.thread = QThread()
        self.worker = AudioWorker(audio_path)
        self.worker.moveToThread(self.thread)
        self.worker.dataLoaded.connect(self.plot_widget.update_plot)
        self.worker.errorOccurred.connect(self.show_error_message)
        self.thread.started.connect(self.worker.process_audio)
        self.thread.start()

    def closeEvent(self, event):
        """Clean up threads before closing."""
        self.thread.quit()
        self.thread.wait()
        super().closeEvent(event)

    def show_error_message(self, message):
        """Display error messages from the worker thread."""
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
