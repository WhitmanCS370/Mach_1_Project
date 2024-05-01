import os
from PySide6.QtCore import QThread
from pydub.playback import play

class AudioPlayer(QThread):
    def __init__(self, audio):
        super().__init__()
        self.audio = audio
        self.playing = False

    def run(self):
        play(self.audio)

    def stop(self):
        self.terminate()