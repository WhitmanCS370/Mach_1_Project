from pydub import AudioSegment
from pydub.playback import play
import e123utils

def play_sound_speed(sound_file: str, speed: float) -> None:
    """
        Plays a sound by some percentage faster or slower, the default is 1.0
    """

    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)
    # speed up the sound
    sound = sound.speedup(playback_speed=speed)
    # play the sound
    play(sound)