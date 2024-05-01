import pygame
import time

class AudioPlayer:
    def __init__(self, audio):
        if not pygame.mixer.get_init():
            pygame.mixer.init()  # Initialize the mixer if it's not already initialized
        self.audio = audio
        self.playing = False
        self.start_time = None

    def start(self):
        pygame.mixer.music.load(self.audio.export("temp.mp3", format="mp3"))
        pygame.mixer.music.play()
        self.playing = True
        self.start_time = time.time()

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False

    def resume(self):
        if not self.playing:
            pygame.mixer.music.unpause()
            self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.start_time = None

    def current_position(self):
        if self.playing and self.start_time:
            return (time.time() - self.start_time) * 1000  # Convert to milliseconds
        return 0
