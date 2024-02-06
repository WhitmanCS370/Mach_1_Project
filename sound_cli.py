import os
import sys

import Commands as cd
import simpleaudio as sa

def check_extension(sound):
    return sound.endswith(".wav")

def play_sound(sound):
    wave_obj = sa.WaveObject.from_wave_file(sound)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def print_help():
    if len(sys.argv) > 2:
        print(f"Unrecognized command: {sys.argv[2]} Please just use the following format: -h or --help.")
        sys.exit(1)

    for command, description in cd.COMMANDS.items():
        print(f"{command}: {description}")

def list_sounds():
    if len(sys.argv) > 2:
        print(f"Unrecognized command: {sys.argv[2]} Please just use the following format: -l or --list.")
        sys.exit(1)

    for sound in os.listdir("./sounds"):
        print(sound)

def play_sound_arg():
    if len(sys.argv) != 3:
        print("Invalid number of arguments. Please use the following format: -p <sound> or --play <sound>.")
        sys.exit(1)

    sound = sys.argv[2]
    if check_extension(sound):
        play_sound(sound)
    else:
        print("Invalid sound file format. Please use a .wav file.")

if __name__ == "__main__":
    commands = {
        "-h": print_help,
        "--help": print_help,
        "-l": list_sounds,
        "--list": list_sounds,
        "-p": play_sound_arg,
        "--play": play_sound_arg
    }

    try:
        command = sys.argv[1]
        commands[command]()
    except (IndexError, KeyError):
        print("Invalid command. Use -h or --help for help.")
        sys.exit(1)