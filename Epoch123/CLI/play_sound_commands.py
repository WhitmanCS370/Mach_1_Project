from pydub import AudioSegment
from pydub.playback import play
import os
import numpy as np
import glob

import Epoch123.GUI.e123utils as e123utils

def play_sound(sound_file: str) -> None:
    """
        Plays a specific sound file
    """

    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    print(main_sound_dir + sound_file)
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)
    # play the sound
    play(sound)


def play_sound_simultaneously(sounds_list: list) -> None:
    """
        Plays a list of sounds simultaneously
    """

    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # create an empty sound object
    sounds = AudioSegment.empty()
    for sound_f in sounds_list:
        # check that the file is a wav file
        if not e123utils.is_valid_extension(sound_f):
            print(f"Invalid file extension: {sound_f}. Only .wav files are supported.")
            continue
        # load the sound file
        sounds += AudioSegment.from_wav(main_sound_dir + sound_f)
    # play the sounds
    play(sounds)


def play_sound_sequentially(sounds_list: list) -> None:
    """
        Plays a list of sounds sequentially
    """

    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    for sound_f in sounds_list:
        # check that the file is a wav file
        if not e123utils.is_valid_extension(sound_f):
            print(f"Invalid file extension: {sound_f}. Only .wav files are supported.")
            continue
        # load the sound file
        sound = AudioSegment.from_wav(main_sound_dir + sound_f)
        # play the sound
        play(sound)


def play_random_sound(sound_dir: str = None) -> None:
    """
        Plays a random sound file from the main sound directory if no specific subdirectory is provided
    """
    # check that the sound directory exists
    # get the ESMD path
    main_sound_dir = e123utils.get_main_sound_dir_path()
    
    # if no sound directory is provided, use the main sound directory
    if sound_dir is None:
        # play some random sound from the ESMD
        sound_files = glob.glob(main_sound_dir + "/**/*.wav", recursive=True)
        sound_file = np.random.choice(sound_files)
        sound = AudioSegment.from_wav(sound_file)
        # print what sound is being played 
        print(f"Playing random sound: {sound_file}")
        play(sound)
    else:
        # check that the sound directory exists
        sound_dir_path = os.path.join(main_sound_dir, sound_dir)
        if not os.path.isdir(sound_dir_path):
            print(f"Invalid sound directory: {sound_dir}")
            return
        # play some random sound from the specified sound directory
        # assuming the subdirectories don't have subdirectories
        sound_files = glob.glob(sound_dir_path + "/*.wav")
        sound_file = np.random.choice(sound_files)
        sound = AudioSegment.from_wav(sound_file)
        # print what sound is being played 
        print(f"Playing random sound: {sound_file}")
        play(sound)


def play_sound_reverse(sound_file: str) -> None:
    """
        Plays a sound file in reverse
    """

    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)
    # reverse the sound
    sound = sound.reverse()
    # play the sound
    play(sound)


def play_sound_speed(sound_file: str, speed: float) -> None:
    """
        Plays a sound by by some percentage faster or slower, the default is 1.0
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


def play_random_sound_snippet(sound_file: str) -> None:
    """
        Plays a random snippet of a sound file
    """

    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)
    # get the duration of the sound
    sound_duration = len(sound)
    # get a random snippet of the sound
    start_time = np.random.randint(0, sound_duration)
    end_time = np.random.randint(start_time, sound_duration)
    sound_snippet = sound[start_time:end_time]
    # play the sound snippet
    play(sound_snippet)


def play_sound_snippet(sound_file: str, start_time: int, end_time: int) -> None:
    """
        Plays a snippet of a sound file
    """

    # check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        print("Invalid file extension. Only .wav files are supported.")
        return
    # get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # load the sound file
    sound = AudioSegment.from_wav(main_sound_dir + sound_file)
    # get the duration of the sound
    sound_duration = len(sound)
    # check that the start and end times are valid
    if start_time < 0 or start_time > sound_duration:
        print("Invalid start time.")
        return
    if end_time < 0 or end_time > sound_duration:
        print("Invalid end time.")
        return
    if start_time >= end_time:
        print("Invalid start and end times.")
        return
    # get the sound snippet
    sound_snippet = sound[start_time:end_time]
    # play the sound snippet
    play(sound_snippet)

