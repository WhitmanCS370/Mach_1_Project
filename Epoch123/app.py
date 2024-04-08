from cli import CLI

from play_sound_commands import play_sound
from sound_dir_commands import list_sounds
from e123_utils import *
import sys

if __name__ == "__main__":
    sounds = ['coffee/coffee-slurp-2.wav', 'toast/toaster-2.wav']
    # play_sound_simultaneously(sounds)

    # stri = get_main_sound_dir_path()
    # play_sound(sounds[0])

    # curses.wrapper(sound_visualize, 'toast/toaster-2.wav')

    list_sounds()

    # search_sound_dir()
    # cli = CLI(sys.argv)
    # cli.run()