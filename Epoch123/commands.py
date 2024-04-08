
COMMANDS = {
    "-h": "Prints all the available commands",
    "--help": "Prints all the available commands",
    "-l": "Lists all the available sounds",
    "--list": "Lists all the available sounds",
    "-p": {
        "description": "Plays a sound file",
        "subcommands": {
            "-sm": "Plays multiple sounds at the same time",
            "-sq": "Plays sounds sequentially",
            "-rand": "Plays a random sound",
            "-rand -snp": "Plays a random sound snippet",
            "-rv": "Plays a sound file in reverse",
            "-speed": {
                "description": "Plays a sound at a specific speed",
                "subcommands": {
                    "-fast": "Plays sound at double speed",
                    "-slow": "Plays sound at half speed"
                }
            },
            "<sound>": "Plays a specific sound"
        }
    },
    "--play": "Plays a sound file",
    "-rn": "Renames a sound file",
    "--rename": "Renames a sound file",
}