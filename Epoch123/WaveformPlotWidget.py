import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QHBoxLayout
from PySide6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import logging
from AudioManager import AudioManager
from Button import Button

class WaveformPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.selected_region = None
        self.selection_rect = None
        self.line = None
        self.audio_cache = {}
        self.set_timer()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def setup_plot(self):
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.set_facecolor('black')
        self.figure.patch.set_facecolor('black')
        self.ax.tick_params(axis='x', colors='orange', direction='out', labeltop=True, labelbottom=False)
        self.ax.tick_params(axis='y', colors='orange', direction='out', labelright=False, labelleft=True)
        self.ax.grid(color='orange', linestyle='-', linewidth=0.25, alpha=0.5)
        self.ax.set_axisbelow(False)
        
        # draw a vertical line to represent the current time
        self.position_line = self.ax.axvline(0, color='gray', lw=1)
        self.position_line.set_zorder(3) 

        self.span_selector = SpanSelector(self.ax, self.on_select, 'horizontal', useblit=True, props=dict(alpha=0.3, facecolor='yellow'))


    def update_plot(self, data, fs, audio):
        try:
            if self.parent.audio_manager and self.parent.audio_manager.playing:
                self.parent.audio_manager.stop()

            self.audio = audio
            self.data = data
            self.fs = fs
            data_length = len(data)
            if data_length == 0:
                raise ValueError("Data array is empty")

            x_data = np.arange(data_length)
            if self.line is None:
                self.setup_plot()
                self.line, = self.ax.plot(x_data, self.data, color='purple', lw=0.5)
            else:
                self.line.set_data(x_data, self.data)
            self.position_line.set_xdata([0])
            self.ax.set_xlim(0, data_length)
            self.set_ticks()
            self.canvas.draw_idle()
            self.canvas.blit(self.ax.bbox)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating plot: {e}")
            logging.error(f"Error updating plot: {e}")


    def set_ticks(self):
        xticks = np.linspace(0, len(self.data), 10)
        self.ax.set_xticks(xticks)
        yticks = np.linspace(-1.5, 1.5, 15)
        self.ax.set_yticks(yticks)
        a_duration = self.audio.duration_seconds
        time = np.linspace(0, a_duration, 10)
        xtick_labels = np.char.mod('%.2f', time)  # Use a vectorized operation to create the labels
        xtick_labels[0] = ''
        self.ax.set_xticklabels(xtick_labels, color='orange', fontsize=8, ha='left', va='bottom', y=0.01)
        yticks_labels = np.char.mod('%.1f', yticks)  # Use a vectorized operation to create the labels
        yticks_labels[0] = ''
        yticks_labels[-1] = ''
        self.ax.set_yticklabels(yticks_labels, color='orange', fontsize=8, ha='left', va='top', x=0.02)
    
    def on_select(self, xmin, xmax):
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None

        if xmax - xmin > 1:  # Only consider selections larger than 1 unit
            self.selected_region = (xmin, xmax)
            self.selection_rect = self.ax.axvspan(xmin, xmax, color='blue', alpha=0.3)
            self.position_line.set_xdata([xmin])
        else:
            self.position_line.set_xdata([0])  # Set position line back to 0 if selection is unselected

        # Restore the background
        self.canvas.restore_region(self.background)

        # Redraw just the selection rectangle and position line
        if self.selection_rect:
            self.ax.draw_artist(self.selection_rect)
        self.ax.draw_artist(self.position_line)

        # Blit the canvas
        self.canvas.draw_idle()
        self.canvas.blit(self.ax.bbox)

    def clear_selection(self):
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None
            self.selected_region = None
            self.position_line.set_xdata([0])
            self.canvas.draw_idle()

    def on_click(self, event):
        # Check if a region is selected and if the click is inside the plot
        if self.selected_region and event.inaxes == self.ax:
            xmin, xmax = self.selected_region
            if event.xdata < xmin or event.xdata > xmax:
                # The click is outside the selected region, clear the selection
                self.clear_selection()

    
    def audio_buttons(self):
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons = [
            Button(label, func, setFixedWidth=75) 
            for label, func in [
                ("▶", self.play_audio), 
                ("⏹", self.stop_audio), 
                ("⏸", self.pause_audio), 
                ("▶⏸", self.resume_audio)
            ]
        ]
        for button in buttons:
            buttons_layout.addWidget(button)
        return buttons_widget

    def stop_audio(self):
        self._audio_manager_action('stop')
        self.timer.stop()

    def pause_audio(self):
        self._audio_manager_action('pause')
        self.timer.stop()

    def resume_audio(self):
        self._audio_manager_action('resume')
        self.timer.start(100)

    def _audio_manager_action(self, action):
        if self.parent.audio_manager:
            getattr(self.parent.audio_manager, action)()

    def set_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position_line)
    
    def play_audio(self):
        try:
            if self.parent.audio_manager:
                self.parent.audio_manager.stop()
            if self.selected_region:
                start_ms = self.selected_region[0] / self.audio.frame_rate * 1000
                end_ms = self.selected_region[1] / self.audio.frame_rate * 1000
                segment = self.audio[start_ms:end_ms]
                # Create audio player with the starting frame as the selected region start
                self.parent.audio_manager = AudioManager(segment, start_frame=self.selected_region[0])
                self.position_line.set_xdata(self.selected_region[0])
            else:
                segment = self.audio
                self.parent.audio_manager = AudioManager(segment)
            self.parent.audio_manager.start()
            self.timer.start(50)  # Adjusted to a fixed interval for smoother updates
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error playing audio: {e}")
            logging.error(f"Error playing audio: {e}")

    def update_position_line(self):
        if self.parent.audio_manager and self.parent.audio_manager.playing:
            current_sample = self.parent.audio_manager.current_frame()
            if self.selected_region:
                sample_within_selected = self.selected_region[0] <= current_sample <= self.selected_region[1]
                if not sample_within_selected:
                    self.parent.audio_manager.stop()
                    self.timer.stop()
                    self.position_line.set_xdata(self.selected_region[0])  # Reset to start of the selection
                else:
                    self.position_line.set_xdata(current_sample)
            else:
                self.position_line.set_xdata(current_sample)
            self.canvas.draw_idle()