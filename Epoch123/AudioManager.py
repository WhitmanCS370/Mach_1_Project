import numpy as np
import soundfile as sf
import pygame as pg
import os
import tempfile
import logging
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QObject, Signal, QThread, QTimer
from pydub import AudioSegment
from GUIElements import Button
import time 

logging.basicConfig(level=logging.INFO)

class AudioProcessor(QObject):
    data_loaded = Signal(np.ndarray, float, object)
    error_occurred = Signal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def process_audio(self):
        """Process the audio file and emit results or errors."""
        try:
            data, samplerate = sf.read(self.audio_path, always_2d=True)
            audio_segment = AudioSegment.from_file(self.audio_path)

            # If audio is stereo, take the mean of both channels to downmix to mono
            if data.shape[1] > 1:
                data = np.mean(data, axis=1)

            self.data_loaded.emit(data, samplerate, audio_segment)
        except Exception as e:
            error_message = f"Error processing audio: {e}"
            self.error_occurred.emit(error_message)
            logging.error(error_message)


class AudioPlayer(QThread):
    error = Signal(str)
    update_position = Signal(int)
    playback_finished = Signal()  # Signal to indicate playback has finished

    def __init__(self, audio_path=None, sample_rate=0, audio_data=None):
        super().__init__()
        self.audio_path = audio_path
        self.sample_rate = sample_rate
        self.audio_data = audio_data
        self.temp_file = None
        self.playing = False
        self.start_time = None
        self.start_frame = 0
        self.pause_time = 0
        self.set_initial_frame(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.emit_position)
        self.timer.setInterval(50)  # Update every 100 ms
        if not pg.mixer.get_init():
            pg.mixer.init()

    def set_initial_frame(self, frame):
        """Set the initial frame to start playback from."""
        self.initial_frame = frame

    def emit_position(self):
        if pg.mixer.music.get_busy():
            position = pg.mixer.music.get_pos()  # Get current position in milliseconds
            self.update_position.emit(position + self.initial_frame * (1000 / self.sample_rate))
        else:
            self.playback_finished.emit()
            self.timer.stop()

    def set_audio(self, audio, audio_data, sample_rate, audio_path):
        self.audio = audio
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.audio_path = audio_path

    def set_audio_data(self, audio_data, sample_rate=0):
        self.audio_data = audio_data
        self.sample_rate = sample_rate

    def start(self):
        self.playing = True
        try:
            if self.audio_data is not None:
                # Write the audio data to a temporary file
                self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                sf.write(self.temp_file.name, self.audio_data, self.sample_rate)
                pg.mixer.music.load(self.temp_file.name)
                pg.mixer.music.play()
                self.start_time = time.time()
                self.timer.start()
            else:
                logging.error("No audio data to play")
        except Exception as e:
            self.error.emit(str(e))
            logging.error(f"Error playing audio: {e}")
        finally:
            self.cleanup()
            self.is_playing = False

    def stop(self):
        if pg.mixer.get_init():
            pg.mixer.music.stop()
        self.cleanup()
        self.timer.stop()
        self.playback_finished.emit()
        self.playing = False

    def pause(self):
        try:
            if pg.mixer.get_init() and self.playing:
                pg.mixer.music.pause()
                self.pause_time = pg.mixer.music.get_pos()
                self.timer.stop()
                self.playing = False
        except Exception as e:
            self.error.emit(str(e))
            logging.error(f"Error pausing audio: {e}")

    def resume(self):
        try:
            if pg.mixer.get_init() and not self.playing:
                pg.mixer.music.unpause()
                self.start_time = self.start_time + (pg.mixer.music.get_pos() - self.pause_time)
                self.timer.start()
                self.playing = True
        except Exception as e:
            self.error.emit(str(e))
            logging.error(f"Error resuming audio: {e}")

    def cleanup(self):
        if self.temp_file:
            os.unlink(self.temp_file.name)
            self.temp_file = None

class AudioControlWidget(QWidget):
    def __init__(self, audio_player, parent=None):
        super().__init__(parent)
        self.audio_player = audio_player
        self.buttons_layout = QHBoxLayout()
        self.setLayout(self.buttons_layout)
        self.init_ui()
        

    def init_ui(self):
        self.buttons_widget = QWidget()
        button_actions = {
            "▶": self.audio_player.start,
            "⏹": self.audio_player.stop,
            "⏸": self.audio_player.pause,
            "▶⏸": self.audio_player.resume,
        }
        for label, func in button_actions.items():
            button = self.create_button(label, func)
            self.buttons_layout.addWidget(button)

    def create_button(self, label, func):
        button = Button(label, func, setFixedWidth=75)
        return button