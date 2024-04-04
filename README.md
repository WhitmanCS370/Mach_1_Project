# Mach 1 Team Project 


# Epoch 1

## Team Members Roles
- Uli: Driver for implementing functional requirements 
- Molly: Tested the requirements.
- Marlyn: Added documentation and cleaned up code.
- Clara: Guided Uli as to what needed to be implemented.

We were all present for the implementation of functional requirements.

## Progress Sumary
We have finished Epoch 1.

## Instructions to Run
```python
COMMANDS = {
  "-h or --help": "Prints all the available commands",
  "-l or --list": "Lists all the available sounds",
  "-p or --play (-sm or -sq) <sounds>": "Plays a sound file, -sm plays multiple sounds at the same time, -sq plays sounds sequentially",
  "-r or --rename <sound> <new_name>": "Renames a sound file"
}
```

## How to use CLI

Run the following command if you want a list of all commands
```
python sound_cli.py -h
```

Run the following command if you want to list all files in a given directory

```
python sound_cli.py -l sounds
```
### Example Usage to play sound
```
python sound_cli.py -p <sounds folder>/<sound>.wav
```

## Testing
Went to the command line and test each command. We inputed corect and wrong command formats to check the commands work and if the wrong command format was given, it would print the error statement.

## Reflection
We found implementing playing sounds simultaneously to be challenging. We were having trouble getting them to start at the same time. We takled this by doing research and testing. In the future, we plan on further cleaning up code and adding more commands if the need arises.
