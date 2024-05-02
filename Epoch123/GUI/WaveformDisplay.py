from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QComboBox, QLabel
from PySide6.QtCore import QTimer, Qt
from pydub import AudioSegment
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from AudioPlayer import AudioPlayer
from Button import Button

class WaveformDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = None
        self.selected_region = None  # To store the selected region (start, end)
        self.selection_rect = None  # Visual representation of the selected region
        # self.set_plot()

    def set_plot(self):
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.ax.set_xlim(0, len(self.data))
        self.ax.set_ylim(-1, 1)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.set_facecolor('black')
        self.figure.patch.set_facecolor('black')
        self.ax.tick_params(axis='x', colors='orange', direction='out', labeltop=True, labelbottom=False)
        self.ax.tick_params(axis='y', colors='orange', direction='out', labelright=False, labelleft=True)
        self.position_line = self.ax.axvline(x=0, color='gray', linewidth=1)
        self.ax.grid(color='orange', linestyle='-', linewidth=0.25, alpha=0.5)
        self.ax.set_axisbelow(False)
        self.span_selector = SpanSelector(self.ax, self.on_select, 'horizontal', useblit=True, minspan=0)

    def on_select(self, xmin, xmax):
        # Check if it's a click without significant drag
        if abs(xmax - xmin) < 1:  # Adjust this threshold based on your data scale
            self.clear_selection()
        else:
            self.selected_region = (int(xmin), int(xmax))
            if self.selection_rect:
                self.selection_rect.remove()  # Remove previous rectangle if exists
            self.selection_rect = self.ax.axvspan(xmin, xmax, color='yellow', alpha=0.3)
            self.position_line.set_xdata(xmin)  # Set position line to the start of the selected region
            self.canvas.draw_idle()

    def clear_selection(self):
        if self.selected_region:
            self.selected_region = None
            if self.selection_rect:
                self.selection_rect.remove()  # Remove the selection rectangle
                self.selection_rect = None
            self.position_line.set_xdata(0)
            self.canvas.draw_idle()
            print("Selection cleared")
    def set_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position_line)

    def set_data(self, file_path):
        self.audio = AudioSegment.from_file(file_path)
        data = np.array(self.audio.get_array_of_samples())
        self.data = data / np.max(np.abs(data))  # Normalization

    def play_audio(self, audio):
        if self.window.audio_player:
            self.window.audio_player.stop()
        if self.selected_region:
            start_ms = self.selected_region[0] / self.audio.frame_rate * 1000
            end_ms = self.selected_region[1] / self.audio.frame_rate * 1000
            segment = self.audio[start_ms:end_ms]
            # Create audio player with the starting frame as the selected region start
            self.window.audio_player = AudioPlayer(segment, start_frame=self.selected_region[0])
            self.position_line.set_xdata(self.selected_region[0])
        else:
            segment = self.audio
            self.window.audio_player = AudioPlayer(segment)
        self.window.audio_player.start()
        self.timer.start(50)  # Adjusted to a fixed interval for smoother updates

    def update_position_line(self):
        if self.window.audio_player and self.window.audio_player.playing:
            current_sample = self.window.audio_player.current_frame()
            if self.selected_region:
                sample_within_selected = self.selected_region[0] <= current_sample <= self.selected_region[1]
                if not sample_within_selected:
                    self.window.audio_player.stop()
                    self.timer.stop()
                    self.position_line.set_xdata(self.selected_region[0])  # Reset to start of the selection
                else:
                    self.position_line.set_xdata(current_sample)
            else:
                self.position_line.set_xdata(current_sample)
            self.canvas.draw_idle()

    def set_x_ticks_time(self):
        xticks = np.linspace(0, len(self.data), 10)  
        self.ax.set_xticks(xticks)
        time = np.linspace(0, self.audio.duration_seconds, 10)
        xtick_labels = [f"{x:.2f}" for x in time]
        xtick_labels[0] = ''
        self.ax.set_xticklabels(xtick_labels, color='orange', fontsize=8, ha='left', va='bottom', y=-0.05)

    def set_y_ticks_noramalized(self):
        yticks = np.linspace(-1, 1, 10)
        self.ax.set_yticks(yticks)
        yticks_labels = [f"{x:.1f}" for x in yticks]
        self.ax.set_yticklabels(yticks_labels, color='orange', fontsize=8, ha='left', va='top', x=0.02,)

    def audio_buttons(self):
        # Add the audio buttons with ascii characters

        self.play_button = Button("▶", lambda: self.play_audio(self.audio), setFixedWidth=75)
        self.pause_button = Button("⏸", self.pause_audio, setFixedWidth=75)
        # >||
        self.resume_button = Button("▶⏸", self.resume_audio, setFixedWidth=75)

        self.audio_button_layout = QHBoxLayout()
        self.audio_button_layout.addWidget(self.play_button)
        self.audio_button_layout.addWidget(self.pause_button)
        self.audio_button_layout.addWidget(self.resume_button)

        self.layout.addLayout(self.audio_button_layout)

    def stop_audio(self):
        if self.window.audio_player:
            self.window.audio_player.stop()
        self.position_line.set_xdata(0)
        self.canvas.draw_idle()
        self.timer.stop()  # Ensure the timer is stopped when audio is stopped

    def pause_audio(self):
        if self.window.audio_player:
            self.window.audio_player.pause()
        self.timer.stop()

    def resume_audio(self):
        if self.window.audio_player:
            self.window.audio_player.resume()
        self.timer.start(100)
        

# WaveformDisplay for the FileNavigation class
class WaveformDisplayFN(WaveformDisplay):
    def __init__(self, window, file_path):
        super().__init__()
        self.file_path = file_path
        self.window = window

        # add the file name as a label
        self.file_name_label = QLabel(file_path.split('/')[-1])
        # center the label
        self.file_name_label.setAlignment(Qt.AlignCenter)
        # set the font size
        self.file_name_label.setStyleSheet("font-size: 24pt;")

        # # remove the margins
        # self.file_name_label.setContentsMargins(0, 0, 0, 0)

        # set the label above the waveform
        self.layout.addWidget(self.file_name_label)
        # self.layout.addWidget(self.canvas)


        self.set_data(file_path)
        self.set_plot()
        self.set_x_ticks_time()
        self.set_y_ticks_noramalized()
        self.set_timer()

        self.ax.plot(self.data, lw=0.3, color='purple')


        self.canvas.draw()
        self.audio_buttons()

        meta_data = self.window.metaData.get_file_metadata(file_path)

        # Add the metadata
        self.add_metadata_to_layout(meta_data)

        # add edit sound and edit metadata buttons
        self.add_edit_buttons_to_layout()

    def add_metadata_to_layout(self, meta_data):
        metadata_table = QTableWidget()
        # set the background color to #5C3566
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
        metadata_table.setStyleSheet("""
            QTableView {
                gridline-color: #ffffff;
                background-color: #151515;
                border: 2px;
                border-color: #ffffff;
                border-style: solid;

            }
        """)

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

        # set the minimum height of the table
        metadata_table.setMinimumHeight(200)

        self.layout.addWidget(metadata_table)

    def add_edit_buttons_to_layout(self):
        self.edit_button = Button("Edit Sound", self.edit_sound)
        self.edit_metadata_button = Button("Edit Metadata", self.edit_metadata)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.edit_metadata_button)
        self.layout.addLayout(button_layout)

    def edit_sound(self):
        self.window.show_sound_editor()
        self.window.sound_editor.set_file_to_edit(self.file_path)

    def edit_metadata(self):
        self.window.show_meta_data_editor()
        self.window.meta_data_editor.set_file_to_edit(self.file_path)

# WaveformDisplay for the SoundEditor class
class WaveformDisplaySE(WaveformDisplay):
    def __init__(self, window, file_path):
        super().__init__()
        self.window = window
        self.file_path = file_path

        self.set_data(file_path)
        self.set_timer()

        # Check if data is not empty
        if self.data is not None and len(self.data) > 0:
            # self.plot()
            self.set_plot()
            self.set_x_ticks_time()
            self.set_y_ticks_noramalized()

            self.ax.plot(self.data, lw=0.3, color='purple')
            self.canvas.draw()

        else:
            print("Data is empty or None")

        self.audio_buttons()

    def plot(self):
        # create a plot and plot the waveform and the frequency vs time 
        self.figure, self.ax = plt.subplots(2, 1, sharex=True)  # Add sharex=True
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Set the figure size and eliminate margins
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        # Check if audio frame rate is not None
        if self.audio.frame_rate is not None:
            # Set axis limits and visibility
            self.ax[0].set_xlim(0, len(self.data))
            self.ax[0].spines['top'].set_visible(False)
            self.ax[0].spines['right'].set_visible(False)
            self.ax[0].spines['bottom'].set_visible(False)
            self.ax[0].spines['left'].set_visible(False)
            self.ax[0].set_facecolor('black')
            self.figure.patch.set_facecolor('black')
            self.ax[0].tick_params(axis='x', colors='orange', direction='out', labeltop=True, labelbottom=False)
            self.ax[0].tick_params(axis='y', colors='orange', direction='out', labelright=False, labelleft=True)
            self.position_line = self.ax[0].axvline(x=0, color='gray', linewidth=1)
            self.ax[0].grid(color='orange', linestyle='-', linewidth=0.25, alpha=0.5)
            self.ax[0].set_axisbelow(False)
            self.ax[0].plot(self.data, lw=0.3, color='purple')

            self.ax[1].set_xlim(0, len(self.data))
            self.ax[1].spines['top'].set_visible(False)
            self.ax[1].spines['right'].set_visible(False)
            self.ax[1].spines['bottom'].set_visible(False)
            self.ax[1].spines['left'].set_visible(False)
            self.ax[1].set_facecolor('black')
            self.figure.patch.set_facecolor('black')
            self.ax[1].tick_params(axis='x', colors='orange', direction='out', labeltop=True, labelbottom=False)
            self.ax[1].tick_params(axis='y', colors='orange', direction='out', labelright=False, labelleft=True)
            self.ax[1].grid(color='orange', linestyle='-', linewidth=0.25, alpha=0.5)
            self.ax[1].set_axisbelow(False)
            self.position_line2 = self.ax[1].axvline(x=0, color='gray', linewidth=1)  # Add position line to second subplot
            NFFT = min(256, len(self.data))
            self.ax[1].specgram(self.data, NFFT=NFFT, Fs=self.audio.frame_rate, noverlap=0, cmap='inferno')

            self.canvas.draw()
        else:
            print("Audio frame rate is None")