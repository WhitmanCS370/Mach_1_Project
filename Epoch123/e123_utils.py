
def get_main_sound_dir_path() -> str:
    """
        Returns the path to the main sound directory
        The Epoch123 Sounds Manager Directory (ESMD)
        ESMD contains all the sound files stored in the Epoch123 application
    """
    import os

    # Determine the path to the directory containing this script
    # script_dir = os.path.dirname(os.path.realpath(__file__))
    # main_sound_dir = os.path.join(script_dir, 'ESMD/')

    main_sound_dir = os.path.join(os.getcwd(), 'ESMD')

    # print(main_sound_dir)

    return main_sound_dir

def is_valid_extension(file_name: str) -> bool:
    """
        Checks if the file has a valid extension
        For the moment, only .wav files are supported
    """
    valid_extensions = ['.wav']
    return any(file_name.endswith(ext) for ext in valid_extensions)