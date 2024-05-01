from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer
from pydub import AudioSegment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from AudioPlayer import AudioPlayer


class WaveformDisplay(QWidget):
    def __init__(self, gui, file_path):
        super().__init__()
        self.gui = gui
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Set the figure size and eliminate margins
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        
        layout.addWidget(self.canvas)

        self.audio = AudioSegment.from_file(file_path)
        data = np.array(self.audio.get_array_of_samples())
        data = data / np.max(np.abs(data))  # Normalization

        # Plot waveform
        self.ax.plot(data, lw=0.3, color='purple')

        # Set axis limits and visibility
        self.ax.set_xlim(0, len(data))
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)

        self.ax.set_facecolor('black')
        self.figure.patch.set_facecolor('black')
        
        # Custom tick settings
        self.ax.tick_params(axis='x', colors='orange', direction='out', labeltop=True, labelbottom=False)
        self.ax.tick_params(axis='y', colors='orange', direction='out', labelright=False, labelleft=True)

        # Set ticks for x-axis as time in seconds
        xticks = np.linspace(0, len(data), 10)
        self.ax.set_xticks(xticks)

        # Set labels for all ticks
        # ignore the first tick as it is at 0
        time = np.linspace(0, self.audio.duration_seconds, 10)
        xtick_labels = [f"{x:.2f}" for x in time]
        xtick_labels[0] = ''
        self.ax.set_xticklabels(xtick_labels, color='orange', fontsize=8, ha='left', va='bottom', y=-0.02)

        # Set ticks for y-axis
        yticks = np.linspace(-1, 1, 10)
        self.ax.set_yticks(yticks)
        yticks_labels = [f"{x:.1f}" for x in yticks]
        self.ax.set_yticklabels(yticks_labels, color='orange', fontsize=8, ha='left', va='bottom', x=0.03)

        # Add grid
        self.ax.grid(color='orange', linestyle='-', linewidth=0.25, alpha=0.5)
        # render the grid atop the data
        self.ax.set_axisbelow(False)

        # Adding a line for current position
        self.position_line = self.ax.axvline(x=0, color='gray', linewidth=1)

        # Timer to update the position line
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position_line)

        # Draw plot
        self.canvas.draw()

        plt.close(self.figure)

        meta_data = self.gui.metaData.get_file_metadata(file_path)

        # Add the metadata
        self.add_metadata_to_layout(meta_data, layout)

        # Add play and pause buttons
        self.add_buttons_to_layout(layout)

    def add_metadata_to_layout(self, meta_data, layout):
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
        
        # Show the grid
        metadata_table.setShowGrid(True)
        metadata_table.setStyleSheet("QTableView {gridline-color: #ffffff;}")

        # have the table grid lines stretch to fill the table
        metadata_table.horizontalHeader().setStretchLastSection(True)
        metadata_table.verticalHeader().setStretchLastSection(True)

        # Set the table to be read-only
        metadata_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set the table to be not selectable
        metadata_table.setSelectionMode(QTableWidget.NoSelection)

        # Hide the headers
        metadata_table.horizontalHeader().setVisible(False)
        metadata_table.verticalHeader().setVisible(False)

        layout.addWidget(metadata_table)

    def add_buttons_to_layout(self, layout):
        self.play_button = QPushButton("▶")  # Play button
        self.pause_button = QPushButton("⏸")  # Pause button
        self.resume_button = QPushButton("⏯")  # Resume button
        self.edit_button = QPushButton("Edit Sound")
        self.edit_metadata_button = QPushButton("Edit Metadata")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.resume_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.edit_metadata_button)
        layout.addLayout(button_layout)
        self.play_button.clicked.connect(lambda: self.play_audio(self.audio))
        self.pause_button.clicked.connect(self.pause_audio)
        self.resume_button.clicked.connect(self.resume_audio)
        self.edit_button.clicked.connect(self.edit_sound)
        self.edit_metadata_button.clicked.connect(self.edit_metadata)

    def update_position_line(self):
        if self.gui.audio_player and self.gui.audio_player.playing:
            current_position = self.gui.audio_player.current_position()
            samples_per_second = self.audio.frame_rate
            total_samples = len(self.audio.get_array_of_samples())
            current_sample = (current_position / 1000) * samples_per_second

            if current_sample >= total_samples:
                current_sample = total_samples  # Ensure it doesn't go beyond the plot
                self.position_line.set_xdata(0)  # Reset the position line to the start
                self.gui.audio_player.stop()  # Stop the audio player
                self.timer.stop()  # Stop the timer
            else:
                self.position_line.set_xdata(current_sample)
            self.canvas.draw_idle()
        else:
            self.position_line.set_xdata(0)
            self.canvas.draw_idle()
            self.timer.stop()

    def play_audio(self, audio):
        if self.gui.audio_player:
            self.gui.audio_player.stop()
        self.gui.audio_player = AudioPlayer(audio)
        self.gui.audio_player.start()
        self.timer.start(50)  # Update more frequently for smoother animation

    def stop_audio(self):
        if self.gui.audio_player:
            self.gui.audio_player.stop()
        self.position_line.set_xdata(0)
        self.canvas.draw_idle()
        self.timer.stop()  # Ensure the timer is stopped when audio is stopped


    def pause_audio(self):
        if self.gui.audio_player:
            self.gui.audio_player.pause()
        self.timer.stop()

    def resume_audio(self):
        if self.gui.audio_player:
            self.gui.audio_player.resume()
        self.timer.start(100)

    def edit_sound(self):
        pass

    def edit_metadata(self):
        self.gui.show_meta_data_editor()