### Introduction ###

grblfeeder is a serial terminal designed for sending gcode files to a microcontroller running grbl.
It makes sending individual commands and also entire files very easy.

grblfeeder has been tested on Windows, with Python 2.7.2 32bit, PySide 1.0.6 32bit and PySerial 2.5.
Testing on Mac OSX 10.6.6 and LinuxMint 11 is my next step.

On load, select the serial terminal your grbl controller is attached to, and set the baud rate.
Click connect, then switch to the second tab to send commands.

To send a file, click Load and select the file you want to send. The file's contents will be added to the queue.
Clicking 'Send One Line' sends one line from the queue to the controller.
Clicking 'Send Continuous' sends a line, waits for an 'ok', and repeats till the queue is empty.

### Requirements ###

To use under Windows, make sure you have these installed:

    Python 		(2.7.2 tested)
    PySide 		(1.0.6 tested)
    PySerial 	(2.5 tested)

To use under Linux (linuxmint/ubuntu lucid to be tested):

    sudo add-apt-repository ppa:pyside
    sudo apt-get update
    sudo apt-get install python
    sudo apt-get install python-serial
    sudo apt-get install python-pyside
	
To use under Mac OS, make sure you have these installed:

    Python               (2.7 to be tested)
    PySide for Mac       (1.0.6 to be tested)
    Qt Libraries for Mac (4.7.4 to be tested)
    PySerial             (2.5 to be tested)
	
### Usage ###

To run grblfeeder, use:

    python grblfeedr.py

### Author ###

timkrins[a]gmail.com
