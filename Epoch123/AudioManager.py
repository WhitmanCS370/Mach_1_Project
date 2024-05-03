import pygame as pg
from PySide6.QtWidgets import QMessageBox
import time
import tempfile
import logging

class AudioManager:
    def __init__(self, audio, start_frame=0):
        if not pg.mixer.get_init():
            pg.mixer.init()  # Initialize the mixer if it's not already initialized
        self.audio = audio
        self.playing = False
        self.start_time = None
        self.start_frame = start_frame  # Save the starting frame

    def current_frame(self):
        if self.playing and self.start_time:
            # Calculate current frame by adding the offset of start_frame
            elapsed_time = time.time() - self.start_time
            current_frame = int(elapsed_time * self.audio.frame_rate) + self.start_frame
            return current_frame
        return self.start_frame

    def current_position(self):
        if self.playing and self.start_time:
            return (time.time() - self.start_time) * 1000  # Convert to milliseconds
        return 0
    
    def start(self):
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp:
                self.audio.export(temp.name, format="mp3")
                pg.mixer.music.load(temp.name)
                pg.mixer.music.play()
            self.playing = True
            self.start_time = time.time()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error starting audio: {e}")
            logging.error(f"Error starting audio: {e}")
            raise

    def pause(self):
        try:
            if self.playing:
                pg.mixer.music.pause()
                self.playing = False
                self.pause_time = time.time()
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error pausing audio: {e}")
            logging.error(f"Error pausing audio: {e}")
            raise

    def resume(self):
        try:
            if not self.playing:
                pg.mixer.music.unpause()
                self.playing = True
                self.start_time += time.time() - self.pause_time
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error resuming audio: {e}")
            logging.error(f"Error resuming audio: {e}")
            raise

    def stop(self):
        try:
            pg.mixer.music.stop()
            self.playing = False
            self.start_time = None
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error stopping audio: {e}")
            logging.error(f"Error stopping audio: {e}")
            raise