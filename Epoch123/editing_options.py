from pydub import AudioSegment
from pydub.playback import play
import e123utils

def change_audio_volume(sound_file: str, dB: float, louderSofter: str) -> None:
    """
        Increases or decreases volume of sound by decibels 
    """

    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)
    
    if louderSofter == 'louder':
        sound = sound + dB
    else:
        sound = sound - dB
    # play the sound
    play(sound)