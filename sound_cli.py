import os
import sys
import random
import wave
import audioop

#import command and simple audio
import Commands as cd
import simpleaudio as sa

def check_extension(sound):
    """ Checks if the sound file has a .wav extension
    
    Parameters:
        sound: an audio file object with .wav exension
    Returns:
        bool: True if file ends with .wav and false if not
    """
    return sound.endswith(".wav")

def print_help():
    """ Prints help message if  arguments for specific command are incorrect

    Parameters:
        None
    Returns:
        None
    """
    if len(sys.argv) > 2:
        print(f"Unrecognized command: {sys.argv[2]} Please just use the following format: -h or --help.")
        sys.exit(1)

    #Prints the commands that are available and their descriptions
    for command, description in cd.COMMANDS.items():
        print(f"{command}: {description}")

def list_sounds():
    """ Prints all available sounds from the sounds folder

    Parameters:
        None
    Returns:
        None
    """
    # check if command line arguments are greater than 2
    if len(sys.argv) > 2:
        print(f"Unrecognized command: {sys.argv[2]} Please just use the following format: -l or --list.")
        sys.exit(1)
    #list the sound files in "./sounds"
    for sound in os.listdir("./sounds"):
        print(sound)

#List to store playback objects for each sound played
play_objects = []

def play_sound(sound):
    """ Plays the given sound file
    
    Parameters:
        sound: an audio file object with .wav extension

    Returns:
        None
    """
    wave_obj = sa.WaveObject.from_wave_file(sound)

    # Stores the object representing playback of a sound
    play_obj = wave_obj.play()
    play_objects.append(play_obj)

#Function that handles different command lines to play the sounds
def play_sound_arg():
    """ Handles different command line flags used to manipulate playback of sounds

    Parameters:
        None
    
    Returns:
        None
    """

    #check if the command line arguments are less than 3
    if len(sys.argv) < 3:
        print("Invalid number of arguments. Please use the following format: -p <sound> or --play <sound>.")
        sys.exit(1)

    # plays sound sequentially if "-sm" flag provided
    if sys.argv[2] == "-sm":
        for i in range(3, len(sys.argv)):
            sound = sys.argv[i]  # add the "sounds/" prefix to the file name
            if check_extension(sound):
                play_sound(sound)
            else:
                print("Invalid sound file format. Please use a .wav file.")
    # plays sound simultaneously if "-sq" flag provided
    elif sys.argv[2] == "-sq":
        for i in range(3, len(sys.argv)):
            sound = sys.argv[i]
            if check_extension(sound):
                wave_obj = sa.WaveObject.from_wave_file(sound)
                play_obj = wave_obj.play()
                play_obj.wait_done()
            else:
                print("Invalid sound file format. Please use a .wav file.")
                break
    else:
        print("Invalid command. Please use type -p -sm or -p -sq.")
        exit(1)

def rename_sound(sound):
    """ Creates a more readable sound file name by replacing "_" and ".wav" with spaces 

    Parameters: 
        sound: an audio file object with .wav extension
    
    Returns:
        sound: the renamed sound
    """
    return sound.replace("_", " ").replace(".wav", "")

def rename_sound_arg():
    """ Handles command line arguments for renaming a sound file

    Parameters:
        None

    Returns:
        None
    """
    #check if command line arguments are less than 4
    if len(sys.argv) < 4:
        print("Invalid number of arguments. Please use the following format: -r <sound> <new_name> or --rename <sound> <new_name>.")
        sys.exit(1)
        
    #Extract the original sound file name and new name from command line
    sound = sys.argv[2]
    new_name = sys.argv[3]

    #Check if file has a valid .wav extension 
    if check_extension(sound):
        os.rename(f"{sound}", f"{new_name}")
    else:
        print("Invalid sound file format. Please use a .wav file.")

def random_snippet(sound):
    """ Plays a random snippet of the given sound. Randomly selects a start
    and end time, ensuring start time is less than end. Snippet is at least 
    0.5 seconds long.

    Parameters:
        sound: an audio file object with .wav extension
    
    Returns:
        obj: the random snippet of sound stored in new wav sound object
    """
    with wave.open(sound, 'rb') as sound_wav:

        # Get audio parameters
        num_frames = sound_wav.getnframes()
        frame_rate = sound_wav.getframerate()
        sample_width = sound_wav.getsampwidth()

        #Calculate maximum snippet duration (in seconds)
        max_snippet_duration = num_frames / frame_rate

        #Get random start time for the snippet
        start_time = random.uniform(0, max_snippet_duration - 0.5)

        #Calculate maximum number of frames for the snippet
        max_snippet_frames = min(num_frames, int((max_snippet_duration - start_time) * frame_rate))

        #Get random end time for the snippet
        end_time = random.uniform(start_time + 1, max_snippet_duration)

        #Convert start and end to frame indices
        start_frame = int(start_time * frame_rate)
        end_frame = int(end_time * frame_rate)

        #Adjust position in wav file
        sound_wav.setpos(start_frame)

        snippet_audio_data = sound_wav.readframes(end_frame - start_frame)

    # Create new wave object from modified audio data
    snippet_wave_obj = sa.WaveObject(snippet_audio_data, num_channels=sound_wav.getnchannels(),
                                      bytes_per_sample=sample_width, sample_rate=frame_rate)

    return snippet_wave_obj

def random_snippet_arg():
    """ Handles command line arguments for getting a random snippet from a sound file

    Parameters:
        None

    Returns:
        None
    """
    # Check if the command line arguments are less than 3
    if len(sys.argv) < 3:
        print("Invalid number of arguments. Please use the following format: -rand <sound>.")
        
def play_back_speed(sound, speed):
    """ Increases speed of a sound file by 2 or decreases speed by half
    
    Parameters:
        sound: an audio file with .wav extension
        speed: either "-fast" to increase speed or "-slow" to decrease playback speed
    
    Returns:
        obj: new wav object with the new frame rate that increases or decreases playback speed
    """
    with wave.open(sound, 'rb') as wav_file:
        #Get the audio parameters
        frame_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()

        #increases frame rate by 2 if flag "-fast" provided
        if speed == "-fast":
            new_frame_rate = int(frame_rate*2)
        #decreases frame rate by 2 if flag "-slow" provided
        elif speed == "-slow":
            new_frame_rate = int(frame_rate/2)
        else:
            print("Not a valid input")

        #Read all frames from wave object    
        frames = wav_file.readframes(wav_file.getnframes())

        #Create new wav object with the new frame rate
        modified_wave_obj = sa.WaveObject(frames, num_channels, sample_width, new_frame_rate)
        
        return modified_wave_obj

def playback_speed_arg():
    """ Handles command line arguments for manipulating playback speed of a sound file

    Parameters:
        None

    Returns:
        None
    """
    # Check if the command line arguments are less than 4
    if len(sys.argv) < 4:
        print("Invalid number of arguments. Please use the following format: -speed <option> <sound>.")
        sys.exit(1)

    #Extract flag that holds speed option
    speed_option = sys.argv[2]

    #Extract sound
    sound = sys.argv[3]

    if check_extension(sound):
        #Determine playback speed based on the speed option
        if speed_option not in ["-fast", "-slow"]:
            print("Invalid speed option. Please use -fast or -slow.")
            sys.exit(1)

        #Modify the playback speed of the audio
        modified_wave_obj = play_back_speed(sound, speed_option)

        if modified_wave_obj:
            #Play the modified audio
            play_obj = modified_wave_obj.play()
            play_obj.wait_done()
        else:
            print("Failed to modify the playback speed.")

def reverse_sound(sound):
    """ Reverses audio data
    
    Parameters:
        sound: an audio file with .wav extension
    
    Returns:
        tuple: A tutple containing the reversed audio data and audio parameters
    """
    with wave.open(sound, 'rb') as wav_file:
        # Get the audio parameters
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_frames = wav_file.getnframes()

        # Read the audio data
        audio_data = wav_file.readframes(num_frames)

    # Reverse the audio data using audioop
    reversed_audio_data = audioop.reverse(audio_data, sample_width)

    return reversed_audio_data, num_channels, sample_width, frame_rate

def reverse_sound_arg():
    # Check if the command line arguments are less than 3
    if len(sys.argv) < 3:
        print("Invalid number of arguments. Please use the following format: -rev <sound>.")
        sys.exit(1)
    
    # Extract the sound file path from the command line
    sound = sys.argv[2]

    # Check if the file has a valid .wav extension 
    if not check_extension(sound):
        print("Invalid sound file format. Please use a .wav file.")
        sys.exit(1)

    try:
        sound_snippet = random_snippet(sound)
        if sound_snippet is not None:
            print("Snippet created successfully.")
            # Play the snippet
            play_obj = sound_snippet.play()
            if play_obj is not None:
                print("Playing snippet...")
                play_obj.wait_done()
                print("Snippet playback completed.")
            else:
                print("Error: Play object is None.")
        else:
            print("Error: Snippet creation failed.")
    except Exception as e:
        print(f"Error occurred: {e}")
        
    if check_extension(sound):
        # Reverse the sound
        reversed_audio_data, num_channels, sample_width, frame_rate = reverse_sound(sound)

        # Create a WaveObject with the reversed audio data
        reversed_wave_obj = sa.WaveObject(reversed_audio_data, num_channels, sample_width, frame_rate)

        # Play the reversed sound
        play_obj = reversed_wave_obj.play()
        play_obj.wait_done()
    else:
        print("Invalid sound file format. Please use a .wav file.")


#maps command line to corresponding function
if __name__ == "__main__":
    commands = {
        "-h": print_help,
        "--help": print_help,
        "-l": list_sounds,
        "--list": list_sounds,
        "-p": play_sound_arg,
        "--play": play_sound_arg,
        "-r": rename_sound_arg,
        "--rename": rename_sound_arg,
        "-rand":random_snippet_arg,
        "-speed": playback_speed_arg,
        "-rev": reverse_sound_arg
    }

    #executes the function based on the command line
    try:
        command = sys.argv[1]
        commands[command]()
    except (IndexError, KeyError):
        print("Invalid command. Use -h or --help for help.")
        sys.exit(1)

    # after all commands have been processed, wait for all sounds to finish
    for play_obj in play_objects:
        play_obj.wait_done()


