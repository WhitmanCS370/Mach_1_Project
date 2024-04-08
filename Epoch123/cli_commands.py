COMMANDS = {
    "help":
    {
        "description": "Prints all the available commands and how to use them",
        "how_to_use": "-h or --help"
    },
    "list":
    {
        "description": "Lists all the available in the main sound directory, if no specific subdirectory is provided",
        "how_to_use": "-l <sound_dir> or --list <sound_dir>"
    },
    "play":
    {
        "description": "Plays a single or multiple sound files depending on the subcommand",
        "subcommands": {
            "-sm":
            {
                "description": "Plays a list of sounds simultaneously",
                "how_to_use": "-p -sm <sound_file1> <sound_file2> ... or --play -sm <sound_file1> <sound_file2> ..."
            },
            "-sq":
            {
                "description": "Plays a list of sounds sequentially",
                "how_to_use": "-p -sq <sound_file1> <sound_file2> ... or --play -sq <sound_file1> <sound_file2> ..."
            },
            "-rand":
            {
                "description": "Plays a random sound file from the main sound directory if no specific subdirectory is provided",
                "how_to_use": "-p -rand <sound_dir> or --play -rand <sound_dir>"
            },
            "-rv":
            {
                "description": "Plays a sound file in reverse",
                "how_to_use": "-p -rv <sound_file> or --play -rv <sound_file>"
            },
            "-speed":
            {
                "description": "Plays a sound by by some percentage faster or slower, the default is 1.0",
                "how_to_use": "-p -speed <sound_file> <speed> or --play -speed <sound_file> <speed>"
            },
            "-vz":
            {
                "description": "Visualizes the audio of a sound file in the terminal",
                "how_to_use": "-p -vz <sound_file> or --play -vz <sound_file>"
            },
            "<sound_file>":
            {
                "description": "Plays a specific sound file",
                "how_to_use": "-p <sound_file> or --play <sound_file>"
            }
        },
    }
}