# Mach 1 Team Project 

## Personal Sound Archive:
CS370 semester long projet implementing sonic archive. Allows a user to upload various sounds, remix and edit sounds, organize sounds, and manage metadata associated with sounds. Sounds must end in a .wav extension.

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
# Epoch 1

## Team Members Roles
- Uli: Driver for implementing functional requirements 
- Molly: Tested the requirements.
- Marlyn: Added documentation and cleaned up code.
- Clara: Guided Uli as to what needed to be implemented.

We were all present for the implementation of functional requirements.

## Progress Sumary
We have finished Epoch 1.
## Testing
Went to the command line and test each command. We inputed corect and wrong command formats to check the commands work and if the wrong command format was given, it would print the error statement.

## Reflection
We found implementing playing sounds simultaneously to be challenging. We were having trouble getting them to start at the same time. We takled this by doing research and testing. In the future, we plan on further cleaning up code and adding more commands if the need arises.

# Epoch 2

## Team Member Roles
- Uli: Implemented part b
- Molly: Implemented part a (enhanced ways to listen to sounds) of epoch 2
- Marlyn: Documentation and  requirements, and use cases
- Clara: Tesing and helped with use cases and requiremnts

## Testing

## Reflection

