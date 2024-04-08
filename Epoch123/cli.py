from command_functions import *

class CLI:
    def __init__(self):
        # Python's equivalent of a switch statement
        self.commands = {
            "-h": help_print_commands,
            "--help": help_print_commands,
            "-l": list_sounds,
            "--list": list_sounds,
            "-p": {
                "-sm": 1,
                "-sq": 2,
                "-rand": 3,
                "-rand": 4,
                "-rv": 5,
                "-speed": {
                    "-fast": 6,
                    "-slow": 7
                },
                "-vz": 8,
                "": 9
            }
        }