### Introduction ###

grblfeeder is a serial terminal designed for sending gcode files to a microcontroller running grbl.
It makes sending individual commands and also entire files very easy.

grblfeeder has been tested on Windows, with Python 2.7.2 32bit, PySide 1.0.6 32bit and PySerial 2.5.

On load, select the serial terminal your grbl controller is attached to, and set the baud rate.
Click connect, then you can switch to the second tab to send commands.

(I intend on smoothing this transition further in the future)

To send a file, click Load and select the file you want to send. The file's contents will be added to the queue.
Clicking 'Send One Line' sends one line from the queue to the controller.
Clicking 'Send Continuous' sends a line, waits for an 'ok', and repeats till the queue is empty.

### Installation ###
To use under Windows, make sure you have these installed:
	Python 		(2.7.2 tested)
	PySide 		(1.0.6 tested)
	PySerial 	(2.5 tested)

To use under Linux (linuxmint/ubuntu lucid half-tested):

	sudo add-apt-repository ppa:pyside
	sudo apt-get update
	sudo apt-get install python
	sudo apt-get install python-serial
	sudo apt-get install python-pyside
	
### Usage ###

To run grblfeeder, use:

python ui.py

### Author ###
by Tim K.
You can probably tell I don't know what I'm doing ;)
