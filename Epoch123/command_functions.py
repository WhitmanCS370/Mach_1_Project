import random
from commands import COMMANDS

import os

import simpleaudio as sa
from mutagen import File
import matplotlib.pyplot as plt
import numpy as np
import wave

def is_valid_extension(sound: str) -> bool:
    """ 
        Checks if the sound file has a .wav extension
    """
    extensions = [ ".wav",".mp3",".mp4",".flac"]

    return any(sound.endswith(ext) for ext in extensions)

def help_print_commands(commands: dict = None) -> None:
    """
        Prints all the available commands and their descriptions along with their subcommands
    """
    # If no commands are provided, then use the default COMMANDS
    if commands is None:
        commands = COMMANDS
    # Iterate through the commands
    for command, value in commands.items():
        # If the value is a dictionary, then print the description and the subcommands
        if isinstance(value, dict):
            print(f'{command}: {value.get("description", "")}\n')
            if 'subcommands' in value:
                help_print_commands(value['subcommands'])
        else:
            print(f'{command}: {value}')

def list_sounds(sound_dir: str = None) -> None:
    """
        Prints all available sound files and directories in the specified sound directory.
        If the sound directory is not provided, prints all the available sounds in the main sound directory,
        including those in subdirectories, formatted as a tree.
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Use the main sound directory if sound_dir is not provided
    if sound_dir is None:
        sound_dir = main_sound_dir
    else:
        sound_dir = os.path.join(main_sound_dir, sound_dir)

    # Print the root directory
    print(os.path.basename(sound_dir))
    
    for root, dirs, files in os.walk(sound_dir):
        level = root.replace(sound_dir, '').count(os.path.sep)
        indent = ' ' * 2 * (level)
        sub_indent = ' ' * 3 * (level + 1)
        
        # Print each directory
        if root != sound_dir:  # Avoid printing the root directory again
            print(f"{indent}|\n{indent}|--- {os.path.basename(root)}")
        
        # Print each file within the directory
        for f in files:
            print(f"  |{sub_indent}|----- {f}")        

def rename_sound_file(old_sound_file_name: str, new_sound_file_name: str) -> None:
    """
        Renames a specified sound file to a new name
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Determine the path to the sound file
    old_sound_file_path = os.path.join(main_sound_dir, old_sound_file_name)
    new_sound_file_path = os.path.join(main_sound_dir, new_sound_file_name)

    # Rename the sound file
    os.rename(old_sound_file_path, new_sound_file_path)

def play_sound_sequentially(sound_files: list) -> None:
    """
        Plays a list of sounds sequentially
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Play each sound file sequentially
    for sound_file in sound_files:
        # check if the sound file has a valid extension
        if not is_valid_extension(sound_file):
            print(f"Invalid sound file: {sound_file}")
            continue

        sound_file_path = os.path.join(main_sound_dir, sound_file)
        wave_obj = sa.WaveObject.from_wave_file(sound_file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

def play_sound_simultaneously(sound_files: list) -> None:
    """
        Plays a list of sounds simultaneously
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    for sound_file in sound_files:
        # check if the sound file has a valid extension
        if not is_valid_extension(sound_file):
            print(f"Invalid sound file: {sound_file}")
            continue

        sound_file_path = os.path.join(main_sound_dir, sound_file)
        wave_obj = sa.WaveObject.from_wave_file(sound_file_path)
        play_obj = wave_obj.play()

def play_random_sound() -> None:
    """
        Chooses a random sound file from the main sound directory and plays it
    """

    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Get a list of all sound files in the main sound directory
    sound_files = [f for f in os.listdir(main_sound_dir) if is_valid_extension(f)]

    # Choose a random sound file
    random_sound_file = random.choice(sound_files)

    # Play the random sound file
    random_sound_file_path = os.path.join(main_sound_dir, random_sound_file)
    wave_obj = sa.WaveObject.from_wave_file(random_sound_file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def play_sound_reverse() -> None:
    """
        Plays a sound file in reverse
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Get a list of all sound files in the main sound directory
    sound_files = [f for f in os.listdir(main_sound_dir) if is_valid_extension(f)]

    # Choose a random sound file
    random_sound_file = random.choice(sound_files)

    # Play the random sound file in reverse
    random_sound_file_path = os.path.join(main_sound_dir, random_sound_file)
    wave_obj = sa.WaveObject.from_wave_file(random_sound_file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

    # Reverse the sound file
    sound_data = wave_obj.to_audio_segment()
    reversed_sound_data = sound_data.reverse()

    # Play the reversed sound file
    play_obj = sa.play_buffer(reversed_sound_data.raw_data, num_channels=sound_data.channels, bytes_per_sample=sound_data.sample_width, sample_rate=sound_data.frame_rate)

def play_sound_speed(sound_file: str, speed: float) -> None:
    """
        Plays a sound file at a specific speed
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Check if the sound file has a valid extension
    if not is_valid_extension(sound_file):
        print(f"Invalid sound file: {sound_file}")
        return

    # Determine the path to the sound file
    sound_file_path = os.path.join(main_sound_dir, sound_file)

    # Load the sound file
    wave_obj = sa.WaveObject.from_wave_file(sound_file_path)

    # Get the sound data
    sound_data = wave_obj.to_audio_segment()

    # Adjust the speed of the sound
    speed_adjusted_sound_data = sound_data.speedup(playback_speed=speed)

    # Play the sound at the adjusted speed
    play_obj = sa.play_buffer(speed_adjusted_sound_data.raw_data, num_channels=sound_data.channels, bytes_per_sample=sound_data.sample_width, sample_rate=sound_data.frame_rate)

def play_random_sound_snippet() -> None:
    """
        Plays a random snippet of a random sound file
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Get a list of all sound files in the main sound directory
    sound_files = [f for f in os.listdir(main_sound_dir) if is_valid_extension(f)]

    # Choose a random sound file
    random_sound_file = random.choice(sound_files)

    # Play a random snippet of the random sound file
    random_sound_file_path = os.path.join(main_sound_dir, random_sound_file)
    wave_obj = sa.WaveObject.from_wave_file(random_sound_file_path)
    play_obj = wave_obj.play()

    # Get the duration of the sound file
    sound_data = wave_obj.to_audio_segment()
    sound_duration = sound_data.duration_seconds

    # Choose a random start time for the snippet
    snippet_start_time = random.uniform(0, sound_duration - 1)

    # Play the snippet
    play_obj = wave_obj.play_from(snippet_start_time)
    play_obj.wait_done()

def play_sound(sound_file: str) -> None:
    """
        Plays a specific sound file
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Check if the sound file has a valid extension
    if not is_valid_extension(sound_file):
        print(f"Invalid sound file: {sound_file}")
        return

    # Determine the path to the sound file
    sound_file_path = os.path.join(main_sound_dir, sound_file)

    # Play the sound file
    wave_obj = sa.WaveObject.from_wave_file(sound_file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def play_sound_snippet(sound_file: str, start_time: float, end_time: float) -> None:
    """
        Plays a snippet of a specific sound file
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Check if the sound file has a valid extension
    if not is_valid_extension(sound_file):
        print(f"Invalid sound file: {sound_file}")
        return

    # Determine the path to the sound file
    sound_file_path = os.path.join(main_sound_dir, sound_file)

    # Load the sound file
    wave_obj = sa.WaveObject.from_wave_file(sound_file_path)

    # Get the sound data
    sound_data = wave_obj.to_audio_segment()

    # Get the duration of the sound file
    sound_duration = sound_data.duration_seconds

    # Check if the start time is within the bounds of the sound file
    if start_time < 0 or start_time > sound_duration:
        print(f"Invalid start time: {start_time}")
        return

    # Check if the end time is within the bounds of the sound file
    if end_time < 0 or end_time > sound_duration:
        print(f"Invalid end time: {end_time}")
        return

    # Check if the end time is greater than the start time
    if end_time <= start_time:
        print("End time must be greater than start time")
        return

    # Play the snippet
    play_obj = wave_obj.play_from(start_time, end_time)
    play_obj.wait_done()

def print_sound_file_metadata(sound_file: str) -> None:
    """
        Prints the metadata of a specific sound file
    """
    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    # Check if the sound file has a valid extension
    if not is_valid_extension(sound_file):
        print(f"Invalid sound file: {sound_file}")
        return

    # Determine the path to the sound file
    sound_file_path = os.path.join(main_sound_dir, sound_file)

    # Load the sound file
    audio_file = File(sound_file_path)

     # Check if the file has tags or metadata
    if audio_file is not None and audio_file.tags is not None:
        for key, value in audio_file.tags.items():
            print(f"{key}: {value}")

def visualize_audio(sound_file: str) -> None:
    """
    Creates a simple audio bar in the terminal showing how loud the sound is.
    """

    # Determine the path to the directory containing this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    main_sound_dir = os.path.join(script_dir, 'sounds')

    sound_file_path = os.path.join(main_sound_dir, sound_file)
    if not os.path.isfile(sound_file_path):
        print(f"Invalid sound file: {sound_file}")
        return

    # Open the audio file
    with wave.open(sound_file_path, 'rb') as wf:
        # Read the whole file into memory
        frames = wf.readframes(wf.getnframes())
        # Convert audio frames to numpy array
        amplitude = np.frombuffer(frames, dtype=np.int16)

        # Calculate the absolute value to get the magnitude
        amplitude = np.abs(amplitude)

        # Split the amplitude array into chunks and calculate the average of each
        chunk_size = len(amplitude) // 50  # Divide into 50 chunks for simplicity
        if chunk_size == 0:  # Prevent division by zero
            chunk_size = 1

        chunks = [amplitude[i:i + chunk_size] for i in range(0, len(amplitude), chunk_size)]
        avg_amplitude = [int(np.mean(chunk)) for chunk in chunks]

        # Normalize the average amplitude to the maximum value to get values between 0 and 1
        max_amplitude = max(avg_amplitude) if avg_amplitude else 1
        normalized_amplitude = [x / max_amplitude for x in avg_amplitude]

        # Display the audio bar
        for amplitude in normalized_amplitude:
            bar = "|" * int(amplitude * 50)  # Scale amplitude to a max of 50 characters
            print(f"{bar}")