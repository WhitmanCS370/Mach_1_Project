import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pydub import AudioSegment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from AudioPlayer import AudioPlayer

class WaveformDisplay(QWidget):
    def __init__(self, gui, file_path, meta_data_obj):
        super().__init__()
        self.gui = gui
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # set the size of the figure
        width, height = self.figure.get_size_inches()
        self.figure.set_size_inches(width, 250/96)

        layout.addWidget(self.canvas)

        audio = AudioSegment.from_file(file_path)
        data = np.array(audio.get_array_of_samples())
        self.ax.plot(data, lw=0.5)
        # set the x label as the duration of the audio
        self.ax.set_xlim(0, len(data))
        # ignore labels on x and y axes
        # self.ax.set_xticks([])
        # self.ax.set_yticks([])
        # remove the white border
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        # have the waveform fill the entire space
        self.ax.set_position([0, 0, 1, 1])
        # set the background color to black
        self.ax.set_facecolor('black')
        # set the figure background color to black
        self.figure.patch.set_facecolor('black')
        # set the grid color to white and make the grid lines be evenly spaced
        # set the spacing between the grid lines to be 1
        self.ax.grid(color='white', linestyle='-', linewidth=0.5, alpha=0.5, which='both')
        # set the grid lines to be behind the waveform
        self.ax.set_axisbelow(True)
        # add grid lines
        
        # draw the waveform
        self.canvas.draw()

        meta_data = meta_data_obj.get_file_metadata(file_path)

        # add the metadata
        metadata_table = QTableWidget()
        metadata_table.setRowCount(3)
        metadata_table.setColumnCount(4)
        metadata_table.setItem(0, 0, QTableWidgetItem("Channels"))
        metadata_table.setItem(0, 1, QTableWidgetItem(str(meta_data["channels"])))
        metadata_table.setItem(0, 2, QTableWidgetItem("Sample Width"))
        metadata_table.setItem(0, 3, QTableWidgetItem(str(meta_data["sample_width"])))
        metadata_table.setItem(1, 0, QTableWidgetItem("Duration"))
        metadata_table.setItem(1, 1, QTableWidgetItem(str(meta_data["duration"]) + " s"))
        metadata_table.setItem(1, 2, QTableWidgetItem("File Size"))
        metadata_table.setItem(1, 3, QTableWidgetItem(str(meta_data["file_size"]) + " bytes"))
        metadata_table.setItem(2, 0, QTableWidgetItem("Sample Rate"))
        metadata_table.setItem(2, 1, QTableWidgetItem(str(meta_data["sample_rate"]) + " Hz"))
        metadata_table.setItem(2, 2, QTableWidgetItem("Tags"))
        tags = ", ".join(meta_data["tags"])
        metadata_table.setItem(2, 3, QTableWidgetItem(tags))
        
        # show the grid
        metadata_table.setShowGrid(True)

        # hide the headers
        metadata_table.horizontalHeader().setVisible(False)
        metadata_table.verticalHeader().setVisible(False)

        layout.addWidget(metadata_table)

        # add play and pause buttons
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.edit_button = QPushButton("Edit Sound")
        self.edit_metadata_button = QPushButton("Edit Metadata")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.edit_metadata_button)
        layout.addLayout(button_layout)
        self.play_button.clicked.connect(lambda: self.play_audio(audio))
        self.pause_button.clicked.connect(self.pause_audio)
        self.edit_button.clicked.connect(self.edit_sound)
        self.edit_metadata_button.clicked.connect(self.edit_metadata)


    def play_audio(self, audio):
        if self.gui.audio_player:
            self.gui.audio_player.stop()
        self.gui.audio_player = AudioPlayer(audio)
        self.gui.audio_player.start()

    def pause_audio(self):
        if self.gui.audio_player:
            self.gui.audio_player.stop()

    def edit_sound(self):
        pass

    def edit_metadata(self):
        pass