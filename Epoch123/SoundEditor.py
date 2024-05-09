from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from GUIElements import Button, LineEdit, GuiWidget, CustomComboBox
from PlotWidget import PlotWidget
from AudioManager import AudioControlWidget
import soundfile as sf
import numpy as np
import scipy.signal as sig
from numpy.fft import fft, ifft
from GUIElements import Slider

class SoundEditor(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.audio_player = parent.audio_player
        self.audio_data, self.audio_file, self.sample_rate = None, None, None

        self.setStyleSheet("background-color: #111111; color: white;")
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Plot and navigation buttons
        self.plot_widget = PlotWidget(audio_player=self.audio_player, parent=self)
        self.set_nav_buttons(layout)
        layout.addWidget(self.plot_widget)

        # Editor options
        self.editor_layout = QVBoxLayout()
        layout.addLayout(self.editor_layout)
        self.set_editor()

    def set_audio_data(self, audio_data, audio_file, sample_rate, audio):
        self.audio_data = audio_data
        self.audio_file = audio_file
        self.sample_rate = sample_rate
        self.audio = audio


    def set_nav_buttons(self, layout):
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(Button("\u2190", self.parent.show_file_nav_widget, setFixedWidth=75))
        nav_layout.addWidget(Button("Save", self.save_audio, setFixedWidth=75))
        nav_layout.addWidget(AudioControlWidget(self.audio_player))
        nav_layout.addWidget(Button("\u23EA", self.audio_player.play_reverse, setFixedWidth=75))
        layout.addLayout(nav_layout)

    def set_editor(self):
        self.create_dropdown("Filter", ["Low Pass", "High Pass", "Band Pass"], self.apply_filter)
        self.create_input("Pitch Shift (Semitones):", "0", self.change_pitch, 200)
        self.create_input("Trim Level (dB):", "0.0", self.trim_audio, 200)
        self.create_slider("Volume", 0, 100, 1, self.audio_player.set_volume, 200)

    def create_dropdown(self, label, items, callback):
        dropdown = CustomComboBox(items)
        dropdown.set_on_change(callback)
        layout = GuiWidget(label_text=f"{label}:", gui_elements=[dropdown])
        self.editor_layout.addWidget(layout)

    def create_input(self, label, placeholder, action, width):
        input_field = LineEdit(placeholder=placeholder, setFixedWidth=50)
        input_field.returnPressed.connect(lambda: action(float(input_field.text())))
        widget = GuiWidget(label_text=label, gui_elements=[input_field], setFixedWidth=width)
        self.editor_layout.addWidget(widget)

    def create_slider(self, label, min_val, max_val, step, callback, width):
        slider = Slider(Qt.Horizontal, min_val, max_val, step, setFixedWidth=width)
        slider.valueChanged.connect(callback)
        layout = GuiWidget(label_text=f"{label}:", gui_elements=[slider], setFixedWidth=width)
        self.editor_layout.addWidget(layout)

    def apply_filter(self, index):
        filter_options = ["Low Pass", "High Pass", "Band Pass"]
        if 0 <= index < len(filter_options):
            selected_filter = filter_options[index]
            try:
                if self.audio_data is None or len(self.audio_data) == 0:
                    QMessageBox.critical(self, "Error", "Audio data is empty.")
                    return

                # Ensure the data is mono for filtering
                if self.audio_data.ndim > 1:
                    self.audio_data = np.mean(self.audio_data, axis=1)  # Averaging stereo to mono

                if selected_filter == "Low Pass":
                    b, a = sig.butter(4, 0.1)
                elif selected_filter == "High Pass":
                    b, a = sig.butter(4, 0.1, btype='high')
                elif selected_filter == "Band Pass":
                    b, a = sig.butter(4, [0.05, 0.15], btype='band')
                else:
                    QMessageBox.critical(self, "Filter Error", "Unknown filter type.")
                    return

                self.plot_widget.undo_stack.append((np.copy(self.audio_data), (self.plot_widget.ax.get_xlim())))
                self.audio_data = sig.filtfilt(b, a, self.audio_data)
                self.audio_player.set_audio_data(self.audio_data, self.sample_rate)  # Update audio player data
                self.plot_widget.update_plot(self.audio_data, self.sample_rate, self.audio)  # Update plot
                QMessageBox.information(self, "Filter Applied", f"{selected_filter} filter applied successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Filter Application Error", f"Failed to apply {selected_filter} filter: {str(e)}")

    def change_pitch(self, semitones):
        """Change pitch using FFT-based method."""
        try:
            factor = 2 ** (semitones / 12)
            self.plot_widget.undo_stack.append((np.copy(self.audio_data), (self.plot_widget.ax.get_xlim())))
            self.audio_data = self.fft_pitch_shift(self.audio_data, factor)
            self.audio_player.set_audio_data(self.audio_data, self.sample_rate)  # Update audio player data
            self.plot_widget.update_plot(self.audio_data, self.sample_rate, None)
            QMessageBox.information(self, "Pitch Shift", "Pitch changed successfully!")
        except Exception as e:
            self.display_error("Failed to change pitch", e)

    def fft_pitch_shift(self, data, factor):
        """Shift the pitch by multiplying its FFT spectrum with a factor."""
        fft_spectrum = fft(data)
        new_fft_spectrum = np.zeros_like(fft_spectrum)
        N = len(fft_spectrum)
        new_indices = (np.arange(N) * factor).astype(int)
        valid = (new_indices < N)
        new_fft_spectrum[new_indices[valid]] = fft_spectrum[valid]
        return ifft(new_fft_spectrum).real

    def trim_audio(self, decibel_level):
        """Trim audio based on the decibel level, applying a threshold relative to the maximum amplitude."""
        if self.audio_data is None or len(self.audio_data) == 0:
            QMessageBox.critical(self, "Error", "No audio data to process.")
            return

        # Calculate the threshold amplitude based on the decibel level
        ref_level = np.max(np.abs(self.audio_data))
        if ref_level == 0:
            return  # Prevent log of zero if audio is silent

        # Convert dB level to a linear amplitude threshold
        threshold = ref_level * (10 ** (decibel_level / 20))

        # Mask array where amplitude is below the threshold
        masked_data = np.where(np.abs(self.audio_data) < threshold, 0, self.audio_data)

        # Save the original state for undo functionality
        self.plot_widget.push_state(self.audio_data)

        # Update audio data
        self.plot_widget.undo_stack.append((np.copy(self.audio_data), (self.plot_widget.ax.get_xlim())))
        self.audio_data = masked_data
        self.audio_player.set_audio_data(self.audio_data, self.sample_rate)
        self.plot_widget.update_plot(self.audio_data, self.sample_rate, self.audio)
        QMessageBox.information(self, "Trim Audio", f"Audio trimmed at {decibel_level} dB successfully!")


    def save_audio(self):
        if self.audio_file:
            sf.write(self.audio_file, self.audio_data, self.sample_rate)
            QMessageBox.information(self, "Save Audio", "Audio saved successfully!")
        else:
            QMessageBox.critical(self, "Error", "No audio file specified.")

    def display_error(self, context, error):
        """Display an error message with context."""
        QMessageBox.critical(self, "Error", f"{context}: {str(error)}")
