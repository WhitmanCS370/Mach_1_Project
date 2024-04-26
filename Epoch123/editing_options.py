from pydub import AudioSegment
from pydub.effects import normalize
from pydub.playback import play
import e123utils

def save_audio_option():
    while True:
        decision = input("Would you like to save this sound? (y/n)")
        if decision == 'y':
            return True
        elif decision == 'n':
            return False
        else:
            print("Invalid response. Please type y/n.")
            

def change_audio_volume(sound_file: str, dB: float, volume: str) -> None:
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
    
    if volume == 'increase':
        sound = sound + dB
    else:
        sound = sound - dB
    # play the sound
    play(sound)

def merge_audio_files(sound_file1: str, sound_file2: str) -> None:
    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file1) or not e123utils.is_valid_extension(sound_file2):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()

    # load the sound file
    sound1 = AudioSegment.from_wav(main_sound_dir + sound_file1) 
    sound2 = AudioSegment.from_wav(main_sound_dir + sound_file2) 

    # combine both files
    combined_sound = sound1 + sound2
    play(combined_sound)  

def trim_audio(sound_file: str, beginning: int, end: int, output_file: str) -> None:
    """
        Cuts an audio from beginning and end in seconds. Saves audio to new file
        given either a full file path or just the name for the edited audio.
    """
    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)  
    # pydub works with milliseconds, change to seconds 
    beginning_cut = beginning * 1000
    end_cut = end * 1000

    if beginning_cut > len(sound) or end_cut > len(sound):
        print(f"Error: Beginning or end time exceed the duration of the audio ({len(sound)/1000} seconds).")
        return
    trimmed_sound = sound[beginning_cut:end_cut]

    # Play the trimmed audio for preview
    print("Previewing trimmed audio...")
    play(trimmed_sound)

    # Prompt user to save editing audio or not
    if save_audio_option():
        trimmed_sound.export(output_file, format = "wav")
        print(f"Trimmed audio save to: {output_file}")
    else:
        print("Trimmed audio not saved.")

