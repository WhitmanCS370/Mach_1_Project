import numpy as np
import soundfile as sf
from PySide6.QtCore import QObject, Signal, QThread
from pydub import AudioSegment
import pygame as pg
import os
import tempfile

class AudioWorker(QObject):
    dataLoaded = Signal(np.ndarray, float, object)
    errorOccurred = Signal(str)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def process_audio(self):
        """Process audio data and emit results, or send an error signal if an exception occurs."""
        try:
            data, samplerate = sf.read(self.audio_path)
            audio_segment = AudioSegment.from_file(self.audio_path)
            self.dataLoaded.emit(data, samplerate, audio_segment)
        except Exception as e:
            self.errorOccurred.emit(f"Error processing audio: {e}")
            
class AudioPlayer(QThread):
    error = Signal(str)

    def __init__(self, audio_path=None, sample_rate=0, audio_data=None):
        super().__init__()
        self.audio_path = audio_path
        self.sample_rate = sample_rate
        self.audio_data = audio_data
        self.temp_file = None
        if audio_path and sample_rate and audio_data is not None:
            pg.mixer.init(frequency=sample_rate)

    def run(self):
        """Write audio data to a temporary file and play it."""
        try:
            self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            sf.write(self.temp_file.name, self.audio_data, self.sample_rate)
            pg.mixer.music.load(self.temp_file.name)
            pg.mixer.music.play()
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        if pg.mixer.get_init():
            pg.mixer.music.stop()
        if self.temp_file:
            os.unlink(self.temp_file.name)

    def pause(self):
        if pg.mixer.get_init():
            pg.mixer.music.pause()

    def unpause(self):
        if pg.mixer.get_init():
            pg.mixer.music.unpause()
