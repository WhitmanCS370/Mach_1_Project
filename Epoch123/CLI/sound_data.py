import os
import wave
import numpy as np
import curses

import Epoch123.GUI.e123utils as e123utils

def sound_visualize(stdscr: 'curses._CursesWindow', sound_file: str) -> None:
    """
        Visualizes the lound levels of a sound file using curses, not real time visualization because of how pydub works.
        Depening on the size of the terminal, the the height of the bars will be adjusted.
    """

    # Check that the file is a wav file
    if not e123utils.is_valid_extension(sound_file):
        stdscr.addstr(0, 0, "Invalid file extension. Only .wav files are supported.")
        stdscr.refresh()
        stdscr.getkey()
        return
    
    # Hide the cursor and clear the screen
    curses.curs_set(0) 
    stdscr.clear()

    # Get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # Check that the sound file exists
    sound_file_path = os.path.join(main_sound_dir, sound_file)
    # Check that the sound file exists
    if not os.path.isfile(sound_file_path):
        stdscr.addstr(0, 0, "Invalid sound file.")
        stdscr.refresh()
        stdscr.getkey()
        return

    # Get window dimensions
    max_y, max_x = stdscr.getmaxyx()

    # Load the sound file and get the amplitude
    with wave.open(sound_file_path, 'rb') as wf:
        frames = wf.readframes(wf.getnframes())
        amplitude = np.frombuffer(frames, dtype=np.int16)
        amplitude = np.abs(amplitude)

    # Normalize and chunk amplitude
    chunk_size = max(1, len(amplitude) // max_x)
    chunks = [amplitude[i:i + chunk_size] for i in range(0, len(amplitude), chunk_size)]
    avg_amplitude = [int(np.mean(chunk)) for chunk in chunks]
    max_amplitude = max(avg_amplitude, default=1)
    normalized_amplitude = [x / max_amplitude for x in avg_amplitude]

    # Ensure we don't try to draw outside of screen
    num_bars_to_draw = min(len(normalized_amplitude), max_x)

    # Draw the bars
    for i in range(num_bars_to_draw):
        bar_length = int(normalized_amplitude[i] * (max_y - 1))  # Adjust bar length to screen height
        for y in range(bar_length):
            try:
                stdscr.addstr(max_y - 1 - y, i, '|')
            except curses.error:
                pass  # Ignore errors writing outside the window
    
    # Refresh the screen and wait for a key press
    stdscr.refresh()
    stdscr.getkey()


def sound_rename(old_name: str, new_name: str) -> None:
    """
        Renames a sound file
    """

    # Get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # Check if the old sound file exists
    old_sound_file_path = os.path.join(main_sound_dir, old_name)
    if not os.path.isfile(old_sound_file_path):
        print(f"Invalid sound file: {old_name}")
        return
    # Check if the new sound file exists
    new_sound_file_path = os.path.join(main_sound_dir, new_name)
    if os.path.isfile(new_sound_file_path):
        print(f"Sound file already exists: {new_name}")
        return
    # Rename the sound file
    os.rename(old_sound_file_path, new_sound_file_path)


def sound_delete(sound_file: str) -> None:
    """
        Deletes a sound file
    """

    # Get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # Check if the sound file exists
    sound_file_path = os.path.join(main_sound_dir, sound_file)
    if not os.path.isfile(sound_file_path):
        print(f"Invalid sound file: {sound_file}")
        return
    # Delete the sound file
    os.remove(sound_file_path)


def sound_print_metadata(sound_file: str) -> None:
    """
        Prints the metadata of a specific sound file
    """

    # Get the main sound directory
    main_sound_dir = e123utils.get_main_sound_dir_path()
    # Check if the sound file has a valid extension
    if not e123utils.is_valid_extension(sound_file):
        print(f"Invalid sound file: {sound_file}")
        return
    # Check if the sound file exists
    sound_file_path = os.path.join(main_sound_dir, sound_file)
    if not os.path.isfile(sound_file_path):
        print(f"Invalid sound file: {sound_file}")
        return
    # Load the sound file
    audio_file = wave.open(sound_file_path, 'rb')
    # Check if the file has tags or metadata
    if audio_file is not None:
        print("File name:", sound_file.split('/')[-1])
        print("Number of channels:", audio_file.getnchannels())
        print("Sample width:", audio_file.getsampwidth())
        print("Frame rate:", audio_file.getframerate())
        print("Number of frames:", audio_file.getnframes())
        print("Compression type:", audio_file.getcomptype())
        print("Compression name:", audio_file.getcompname())
        print("Duration (s):", audio_file.getnframes() / audio_file.getframerate())
        print("Size (bytes):", os.path.getsize(sound_file_path))
        audio_file.close()
    else:
        print(f"No metadata found for sound file: {sound_file}")