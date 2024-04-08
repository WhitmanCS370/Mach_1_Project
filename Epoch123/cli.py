import sys

from play_sound_commands import *
from sound_data import *
from sound_dir_commands import *
from cli_commands import *

class CLI:
    def __init__(self, argv) -> None:
        self.args = argv

        # Python's equivalent of a switch statement
        self.commands = {
            "-h": self.print_help,
            "--help": self.print_help,
            "-l": list_sounds,
            "--list": list_sounds,
            "-p": self.play_sounds,
            "--play": self.play_sounds,
            "-sh": self.search_sound_dir,
            "--search": self.search_sound_dir
        }

    def print_help(self) -> None:
        """
            Prints the help message
        """
        print("Help message")
        # ge the width of the terminal
        terminal_width = os.get_terminal_size().columns
        print("-" * terminal_width)
        for command, data in COMMANDS.items():
            print(f"{command}: {data['description']}\n")
            if "subcommands" in data:
                for subcommand, subdata in data["subcommands"].items():
                    print(f"\t{subcommand}: {subdata['description']}")
                    print(f"\t\t{subdata['how_to_use']}\n")
            else:
                print(f"\t{data['how_to_use']}\n") 

        print("-" * terminal_width)

    def play_sounds(self) -> None:
        """
            Plays sound files
        """
        try:
            subcommand = self.args[2]
            if subcommand in COMMANDS["play"]["subcommands"]:
                sound_file = self.args[3]
                if subcommand == "-sm":
                    play_sound_simultaneously(self.args[3:])
                elif subcommand == "-sq":
                    play_sound_sequentially(self.args[3:])
                elif subcommand == "-rand":
                    play_random_sound(sound_file)
                elif subcommand == "-rv":
                    play_sound_reverse(sound_file)
                elif subcommand == "-speed":
                    play_sound_speed(sound_file, self.args[4])
                elif subcommand == "-vz":
                    curses.wrapper(sound_visualize, sound_file)
                else:
                    print(f"Invalid subcommand. Use -h or --help for help.")
                    sys.exit(1)
            else:
                play_sound(self.args[2])
        except IndexError:
            print("Invalid subcommand. Use -h or --help for help.")
            sys.exit(1)

    def search_sound_dir(self) -> None:
        """
            Searches for a sound file in the main sound directory
        """
        try:
            sound_dir = self.args[2] if len(self.args) > 2 else ''
            search_term = self.args[3] if len(self.args) > 3 else ''
            search_sound_dir(sound_dir=sound_dir, search_term=search_term)
        except IndexError:
            search_sound_dir()

    def run(self) -> None:
        """
            Runs the CLI
        """
        try:
            command = self.args[1]
            subcommand = self.args[2] if len(self.args) > 2 else ""
            if isinstance(self.commands[command], dict):
                if subcommand in self.commands[command]:
                    if callable(self.commands[command][subcommand]):
                        self.commands[command][subcommand]()
                    else:
                        print(f"Invalid subcommand. Use -h or --help for help.")
                        sys.exit(1)
                else:
                    print(f"Invalid subcommand. Use -h or --help for help.")
                    sys.exit(1)
            else:
                self.commands[command]()
        except (IndexError, KeyError):
            print("Invalid command. Use -h or --help for help.")
            sys.exit(1)
    