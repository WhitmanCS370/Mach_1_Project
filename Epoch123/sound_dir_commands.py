import os
import e123_utils

def list_sounds(sound_dir: str = None) -> None:
    """
    Lists all sound files in a specific directory, showing directories and their contents hierarchically.
    """
    # Base directory setup
    sound_dir = os.path.join(e123_utils.get_main_sound_dir_path(), sound_dir or '')
    print(os.path.basename(sound_dir))

    # Function to handle the recursive directory listing with proper indentation
    def list_dir_contents(dir_path, prefix=''):
        nonlocal sound_dir
        entries = os.listdir(dir_path)
        dirs = [d for d in entries if os.path.isdir(os.path.join(dir_path, d))]
        files = [f for f in entries if os.path.isfile(os.path.join(dir_path, f))]

        # Sort directories and files for consistent output
        dirs.sort()
        files.sort()

        entries = dirs + files  # Directories first, then files
        
        for i, entry in enumerate(entries):
            entry_path = os.path.join(dir_path, entry)
            # Determine if this entry is the last in the current directory for proper line ending
            is_last = i == (len(entries) - 1)

            if os.path.isdir(entry_path):
                # For directories, print and recursively list contents
                print(f"{prefix}{'|--- ' if dirs else ''}{entry}")
                next_prefix = prefix + ("    " if is_last else "|   ")
                list_dir_contents(entry_path, next_prefix)
            else:
                # For files, just print
                print(f"{prefix}|--- {entry}")

    list_dir_contents(sound_dir)

def search_sound_dir(sound_dir: str = None) -> None:
    """
    Searches for a sound file in a specific directory.
    """
    # Get the main sound directory
    main_sound_dir = e123_utils.get_main_sound_dir_path()
    sound_dir = os.path.join(main_sound_dir, sound_dir or '')

    # Get the search term
    search_term = input("Enter the search term: ")

    # Function to handle the recursive directory listing with proper indentation
    def search_dir_contents(dir_path):
        nonlocal search_term
        entries = os.listdir(dir_path)
        dirs = [d for d in entries if os.path.isdir(os.path.join(dir_path, d))]
        files = [f for f in entries if os.path.isfile(os.path.join(dir_path, f))]

        # Sort directories and files for consistent output
        dirs.sort()
        files.sort()

        entries = dirs + files  # Directories first, then files

        for entry in entries:
            entry_path = os.path.join(dir_path, entry)

            if os.path.isdir(entry_path):
                # For directories, recursively search contents
                search_dir_contents(entry_path)
            else:
                # For files, check if the search term is in the file name
                if search_term.lower() in entry.lower():
                    print(entry_path)

    search_dir_contents(sound_dir)