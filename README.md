# Mach 1 Team Project 

## Personal Sound Archive:
CS370 semester long project implementing sonic archive. Allows a user to upload various sounds, remix and edit sounds, organize sounds, and manage metadata associated with sounds. Sounds must end in a .wav extension.

## Instructions to Run
First, make sure all modules are installed. A list of required modules can be found in requirements.txt.
Then enter the following command in the terminal to run the program.
```python
python3 Epoch123/app.py
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
- Uli: Implemented part b (ways to characterize and organize sounds) of epoch 2
- Molly: Implemented part a (enhanced ways to listen to sounds) of epoch 2
- Marlyn: Documentation, requirements, and use cases
- Clara: Testing and helped with use cases and requirements

Reflection 
Implementing visualize_audiowas the hardest to implement and the one we struggled with. We were having trouble displaying the audio bar. We did some research and we were able to figure it out. For Epoch 3 we plan to have a GUI.

# Epoch 3

## Team Member Roles
- Uli: Impelmentation part 2, further editing and features of the GUI.
- Molly: Implementation part 1, basic of the GUI
- Marlyn: Requirements and use cases. Documentation
- Clara: Implementation of file navigation and GUI testing. Requirements and use cases.

Reflection
The main challenge of Epoch 3 was implementing the GUI. We inititally tried to implement it with tkinter, but quickly ran into issues with integrating functionality. We were able to address this problem by switching to PySide, which opened up a lot more opportunitites for implementing interesting features such as the waveform. Next steps for the project is to fully integrate audio tags and descriptions into our GUI.
