import pygame
import time

class AudioPlayer:
    def __init__(self, audio, start_frame=0):
        if not pygame.mixer.get_init():
            pygame.mixer.init()  # Initialize the mixer if it's not already initialized
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

    def start(self):
        pygame.mixer.music.load(self.audio.export("temp.mp3", format="mp3"))
        pygame.mixer.music.play()
        self.playing = True
        self.start_time = time.time()

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.pause_time = time.time()  # Add this line

    def resume(self):
        if not self.playing:
            pygame.mixer.music.unpause()
            self.playing = True
            self.start_time += time.time() - self.pause_time  # Add this line

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.start_time = None

    def current_position(self):
        if self.playing and self.start_time:
            return (time.time() - self.start_time) * 1000  # Convert to milliseconds
        return 0
