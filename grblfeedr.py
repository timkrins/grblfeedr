'''
 grblfeedr, a grbl serial sender
 
 timkrins@gmail.com
 
 todo: 
       change *all* signals to new style (not just the clicked's)
       possible mac bug causes 'bus error'?
       incorporate nc code formatting (inches to mm conversion, etc)
       [create immediate stop button in firmware]
       buffer size indicator? might not be possible or useful
       just a note: M codes are recieved and actioned immediately, this could be bad
'''

import sys
import time
import serial
import os

from PySide import QtCore, QtGui
from grblfeedr_ui import *

class MultiSender(QtCore.QThread):
    ''' Continuous queue-sending thread '''
    def __init__(self, parent):
        self.starter = 1
        self.runner = 0
        self.SL_MS = 0.01
        self.parent = parent
        QtCore.QThread.__init__(self, parent)
        
    def run(self):
        while self.starter:
            time.sleep(self.SL_MS)
            if self.runner:
                if(self.parent.got_okay):
                    self.parent.got_okay = False
                    self.emit(QtCore.SIGNAL("nextLine()"))

class SerialProcessor(QtCore.QThread):
    ''' Serial input processing thread '''
    def __init__(self, parent):
        self.starter = 1
        self.runner = 0
        self.SL_MS = 0.01
        self.parent = parent
        QtCore.QThread.__init__(self, parent)
    
    def run(self):
        ''' This thread should not call the GUI thread, only use signals
        eg: regenTermWindow cannot be called directly.                '''
        self.currentline = []
        while self.starter:
            time.sleep(self.SL_MS)
            if self.runner:
                try:
		    self.processLine(self.currentline, self.parent)
		    chunk = self.parent.serialConnection.readline()
		    if(chunk):
		        self.currentline.extend(list(chunk.decode('utf-8')))
		except OSError:
		    print('The operating system returned an error when line was read.')
		except serial.SerialException:
		    print('The serial port returned an error, was the device disconnected?')
		    self.runner = False
            
    def processLine(self, currentline, parent):
        ''' Process the line and check for line feeds '''
        full_line = []
        while ("\n" in currentline) or ("\r" in currentline):
            currentpop = currentline.pop(0)
            full_line.extend(currentpop)
        else:
            if(full_line):
                full_line.pop()
                if(len(full_line) > 1):
                    popnstrip = "".join(full_line).strip()
                    if(popnstrip == "ok"):
                        parent.got_okay = 1
                        parent.common_termAdd(popnstrip, 'lime', italic=True, regen=False)
                    else:
                        parent.common_termAdd(popnstrip, regen=False)
                    self.emit(QtCore.SIGNAL("regen()"))
                full_line = []
        return ""
            
class GrblForm(QtGui.QMainWindow):
    ''' GrblFeedr graphical user interface '''
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
        ''' Variables that will need to be accessed later. '''
        self.file_contents = []
        self.formatted_file_contents = []
        self.termwindow_contents = []
        self.got_okay = 0
        self.file_length = 0.00
        self.file_currentline = 0.00
        
        ''' Set up user interface. '''
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.directory = sys.path[0]+os.sep
        self.setupScreen(self.ui)
        
        ''' Set up threads. '''
        self.thread_sender = MultiSender(self)
        self.thread_sender.start()
        self.thread_processor = SerialProcessor(self)
        self.thread_processor.start()
        
        ''' Set up signals. '''
        self.ui.actionConnect.triggered.connect(self.click_connectButton)
        self.ui.actionLoad_GCode.triggered.connect(self.openFile)
        self.ui.exitButton.clicked.connect(self.close)
        self.ui.exitButton2.clicked.connect(self.close)
        self.ui.exitButton3.clicked.connect(self.close)
        self.ui.exitButton4.clicked.connect(self.close)
        self.ui.loadButton.clicked.connect(self.openFile)
        self.ui.sendOne.clicked.connect(self.click_sendOne)
        self.ui.sendCont.clicked.connect(self.click_sendCont)
        self.ui.sendStop.clicked.connect(self.click_stopSending)
        self.ui.termLine.returnPressed.connect(self.press_Enter)
        self.ui.termLine.cursorPositionChanged.connect(self.clearInput)
        self.ui.clearButton.clicked.connect(self.click_clearQueue)
        self.ui.clearTerm.clicked.connect(self.click_clearTerm)
        self.ui.connectButton.clicked.connect(self.click_connectButton) 
        self.ui.disconnectButton.clicked.connect(self.click_disconnectButton) 
        self.ui.nextScreen.clicked.connect(self.click_nextScreen) 
        
        QtCore.QObject.connect(self.thread_sender, QtCore.SIGNAL("nextLine()"), self.sent_threadSender)
        QtCore.QObject.connect(self.thread_processor, QtCore.SIGNAL("regen()"), self.common_regenTerminal)
        
        self.ui.go_g00.clicked.connect(self.click_go_g00)
        self.ui.go_g01.clicked.connect(self.click_go_g01)
        
        self.ui.go_g90.clicked.connect(self.click_go_g90)
        self.ui.go_g91.clicked.connect(self.click_go_g91)
        
        self.ui.go_m03.clicked.connect(self.click_go_m03)
        self.ui.go_m05.clicked.connect(self.click_go_m05)
        
        self.ui.go_m_x01.clicked.connect(self.click_go_m_x01)
        self.ui.go_m_x1.clicked.connect(self.click_go_m_x1)
        self.ui.go_m_x10.clicked.connect(self.click_go_m_x10)
        
        self.ui.go_m_y01.clicked.connect(self.click_go_m_y01)
        self.ui.go_m_y1.clicked.connect(self.click_go_m_y1)
        self.ui.go_m_y10.clicked.connect(self.click_go_m_y10)
        
        self.ui.go_m_z01.clicked.connect(self.click_go_m_z01)
        self.ui.go_m_z1.clicked.connect(self.click_go_m_z1)
        self.ui.go_m_z5.clicked.connect(self.click_go_m_z5)
        
        self.ui.go_p_x01.clicked.connect(self.click_go_p_x01)
        self.ui.go_p_x1.clicked.connect(self.click_go_p_x1)
        self.ui.go_p_x10.clicked.connect(self.click_go_p_x10)
        
        self.ui.go_p_y01.clicked.connect(self.click_go_p_y01)
        self.ui.go_p_y1.clicked.connect(self.click_go_p_y1)
        self.ui.go_p_y10.clicked.connect(self.click_go_p_y10)
        
        self.ui.go_p_z01.clicked.connect(self.click_go_p_z01)
        self.ui.go_p_z1.clicked.connect(self.click_go_p_z1)
        self.ui.go_p_z5.clicked.connect(self.click_go_p_z5)
        
    def gen_macList(self):
        ''' Generates either a serial port listing on Mac OS, or a 256 number range on other OS '''
        if(sys.platform == "darwin"):
            devlist = os.listdir("/dev/")
            devs = ["/dev/"+filename for filename in devlist if 'cu.' in filename]
            return devs
	elif(sys.platform == "linux2"):
            devlist = os.listdir("/dev/")
            devs = ["/dev/"+filename for filename in devlist if 'tty' in filename]
            return devs
        else:
            return range(256)
        
    def common_scanPorts(self):
        ''' Returns all the avaliable COM ports '''
        coms = []
        for port in self.gen_macList():
            try:
                s = serial.Serial(port)
                coms.append( str(s.portstr))
                s.close()
            except serial.SerialException:
                pass
        return coms
 
    def common_regenTerminal(self):
        ''' Updates the terminal window '''
        self.ui.termWindow.setHtml("<br>".join(self.termwindow_contents[-40:]))
        ''' Updates smaller term window '''
        self.ui.termWindow_2.setHtml("<br>".join(self.termwindow_contents[-5:]))

    def common_regenContent(self): 
        ''' Updates the queue window '''
        try:
            if(self.formatted_file_contents[1]):
                self.formatted_file_contents.insert(1,"</font><font color=grey>")
                self.formatted_file_contents.insert(0,"<font color=red size=4><b>>> </font><font color=blue size=4>")
                self.formatted_file_contents.append("</font>")
        except IndexError:
            ''' There were no contents to regenerate '''
            pass
        self.ui.textEdit.setHtml("".join(self.formatted_file_contents[0:30]))
        self.ui.currentProgress.setValue((self.file_currentline/self.file_length)*100)
        
    def common_disableThread(self, thread):
        ''' Disables the thread processing loop '''
        thread.runner = 0
        return True
        
    def common_enableThread(self, thread):
        ''' Enables the thread processing loop '''
        thread.runner = 1
        return True
        
    def common_exitAll(self, event=None):
        ''' Waits for threads to end and quits. '''
        self.thread_sender.starter = 0
        self.thread_sender.wait()
        self.thread_sender.exit()
        self.thread_processor.starter = 0
        self.thread_processor.wait()
        self.thread_processor.exit()
        self.common_finalQuit()
        
    def common_finalQuit(self):
        ''' Quits the application '''
        quit()
		
    def click_stopSending(self):
        ''' Stop Sending has been clicked '''
        ''' Prints 'stopping' to the window, and changes button states. '''
        self.common_disableThread(self.thread_sender)
        self.common_termAdd('-> stopping...')
        self.ui.sendStop.setDisabled(True)
        self.ui.sendCont.setDisabled(False)
        self.ui.sendOne.setDisabled(False)
        self.ui.loadButton.setDisabled(False)
        
    def click_clearTerm(self):
        ''' Clear Terminal button was clicked'''
        ''' Deletes contents of terminal window and updates. '''
        del(self.termwindow_contents[:])
        self.common_regenTerminal()
        
    def click_clearQueue(self):
        ''' Clear Queue button was clicked'''
        ''' Clears the queue and updates. '''
        del(self.file_contents[:])
        del(self.formatted_file_contents[:])
        self.ui.sendCont.setDisabled(True)
        self.ui.sendOne.setDisabled(True)
        self.ui.clearButton.setDisabled(True)
        self.file_length = 1.00
        self.common_regenContent()
        self.common_termAdd('-> queue cleared...')
        self.file_currentline = 0.00
        
    def sent_threadSender(self):
        ''' Send event received from sender thread '''
        try:
            currentliner = self.file_contents.pop(0).strip()
            del(self.formatted_file_contents[0:3])
            self.file_currentline += 1.0
            self.common_regenContent()
            self.common_sendLine(currentliner, color='blue')
        except None:
            self.stopThread('thread_sender')
            
    def click_sendCont(self):
        ''' Send Continuous was clicked. '''
        try:
            if(self.serialConnection):
                self.common_enableThread(self.thread_sender)
                self.ui.sendStop.setDisabled(False)
                self.ui.sendCont.setDisabled(True)
                self.ui.sendOne.setDisabled(False)
                self.ui.loadButton.setDisabled(True)
            else:
                self.ui.tabWidget.setCurrentIndex(0)
        except None:
            self.ui.tabWidget.setCurrentIndex(0)
            
    def click_sendOne(self):
        ''' Send one was clicked '''
        currentliner = self.file_contents.pop(0).strip()
        del(self.formatted_file_contents[0:3])
        self.file_currentline += 1.0
        self.common_regenContent()
        self.common_sendLine(currentliner)
        
    def openFile(self):
        ''' Open file button clicked '''
        try:
            fileName = QtGui.QFileDialog.getOpenFileName(None, u"Select G-Code to send to CNC",u"",u"GCode Files (*.nc *.gc *.ngc);;All Files (*.*)")
            fLoad = open(fileName[0],'r')
            del(self.file_contents[:])
            del(self.formatted_file_contents[:])
            self.ui.clearButton.setDisabled(False)
            self.ui.sendOne.setDisabled(False)
            self.ui.sendCont.setDisabled(False)
            for line in fLoad:
                self.file_contents.append(line)
                formattedline = line+"<br>"
                self.formatted_file_contents.append(formattedline)
            fLoad.close()
            self.file_length = float(len(self.file_contents))
            self.common_regenContent()
        except IOError:
            print('File was either empty or was not opened correctly')
            
    def press_Enter(self):
        ''' Enter button was hit '''
        writeText = self.ui.termLine.text()
        self.common_sendLine(writeText, color='lime')
        self.ui.termLine.clear()
        
    def clearInput(self):
        ''' Clears input of terminal line. '''
        if(self.ui.termLine.text() == "Enter Command"):
            self.ui.termLine.clear()
            
    def common_sendLine(self, message, error='Generic Error', color='red', italic=False, bold=False, regen=True):
        ''' Send one line to the serial port and add it to the terminal window '''
        self.common_termAdd(message, color, italic, bold, regen)
        self.serialConnection.writeTimeout = 0.1
        try:
            self.serialConnection.write((message+"\n").encode('utf-8'))
        except serial.SerialTimeoutException:
            self.common_termAdd('Error: Serial command timed out')
        
    def common_termAdd(self, message, color='yellow', italic=False, bold=False, regen=True):
        ''' Adds a line to the terminal window '''
        messageBuilder = []
        messageBuilder.append('<font color=\"'+color+'\">')
        if italic: messageBuilder.append('<i>')
        if bold:   messageBuilder.append('<b>')            
        messageBuilder.append(message)        
        if bold:   messageBuilder.append('</b>')
        if italic: messageBuilder.append('</i>')
        messageBuilder.append('</font>')
        self.termwindow_contents.append(''.join(messageBuilder))
        if(regen):
            self.common_regenTerminal()

    def click_connectButton(self):
        ''' Connect button was clicked. '''
        serialSelector = self.ui.comboBox.currentText()
        baudSelector = self.ui.comboBox_2.currentText()
        self.common_connect(serialSelector,baudSelector)

    def click_go_g00(self):
        self.common_sendLine(message = 'G00', color = 'orange')
    def click_go_g01(self):
        self.common_sendLine(message = 'G01', color = 'orange')
        
    def click_go_g90(self):
        self.common_sendLine(message = 'G90', color = 'orange')
    def click_go_g91(self):
        self.common_sendLine(message = 'G91', color = 'orange')
        
    def click_go_m03(self):
        self.common_sendLine(message = 'M03', color = 'orange')
    def click_go_m05(self):
        self.common_sendLine(message = 'M05', color = 'orange')
        
    def click_go_m_x01(self):
        self.common_sendLine(message = 'X-0.1', color = 'orange')
    def click_go_m_x1(self):
        self.common_sendLine(message = 'X-1', color = 'orange')
    def click_go_m_x10(self):
        self.common_sendLine(message = 'X-10', color = 'orange')
        
    def click_go_m_y01(self):
        self.common_sendLine(message = 'Y-0.1', color = 'orange')
    def click_go_m_y1(self):
        self.common_sendLine(message = 'Y-1', color = 'orange')
    def click_go_m_y10(self):
        self.common_sendLine(message = 'Y-10', color = 'orange')
        
    def click_go_m_z01(self):
        self.common_sendLine(message = 'Z-0.1', color = 'orange')
    def click_go_m_z1(self):
        self.common_sendLine(message = 'Z-1', color = 'orange')
    def click_go_m_z5(self):
        self.common_sendLine(message = 'Z-5', color = 'orange')
        
    def click_go_p_x01(self):
        self.common_sendLine(message = 'X0.1', color = 'orange')
    def click_go_p_x1(self):
        self.common_sendLine(message = 'X1', color = 'orange')
    def click_go_p_x10(self):
        self.common_sendLine(message = 'X10', color = 'orange')
        
    def click_go_p_y01(self):
        self.common_sendLine(message = 'Y0.1', color = 'orange')
    def click_go_p_y1(self):
        self.common_sendLine(message = 'Y1', color = 'orange')
    def click_go_p_y10(self):
        self.common_sendLine(message = 'Y10', color = 'orange')
        
    def click_go_p_z01(self):
        self.common_sendLine(message = 'Z0.1', color = 'orange')
    def click_go_p_z1(self):
        self.common_sendLine(message = 'Z1', color = 'orange')
    def click_go_p_z5(self):
        self.common_sendLine(message = 'Z5', color = 'orange')

    def common_connect(self, serialPort, serialBaud, serialTimeout=0.01):
        ''' Connects to the serial port '''
        try:
            self.serialConnection = serial.Serial(port=serialPort, baudrate=serialBaud, timeout=serialTimeout)
            self.ui.connectButton.setText("Connected.")
            self.ui.connectButton.setDisabled(True)
            self.ui.disconnectButton.setDisabled(False)
            self.ui.comboBox.setDisabled(True)
            self.ui.comboBox_2.setDisabled(True)
            self.ui.tab.setDisabled(False)
            self.ui.tab_4.setDisabled(False)
            self.ui.actionLoad_GCode.setDisabled(False)
            self.common_enableThread(self.thread_processor)
        except serial.SerialException:
            print('Could not connect to the serial port \"'+serialPort+'\" at baud '+serialBaud+'.')

    def click_disconnectButton(self):
        ''' Disconnect button was clicked. '''
        self.common_disconnect()

    def common_disconnect(self):
        ''' Disconnects from the serial port '''
        try:
            self.common_disableThread(self.thread_processor)
            self.serialConnection.close()
            self.ui.connectButton.setText("Connect")
            self.ui.connectButton.setDisabled(False)
            self.ui.comboBox.setDisabled(False)
            self.ui.actionLoad_GCode.setDisabled(True)
            self.ui.comboBox_2.setDisabled(False)
            self.ui.tab.setDisabled(True)
            self.ui.tab_4.setDisabled(True)
            self.ui.disconnectButton.setDisabled(True)
        except None:
            pass
            
    def click_nextScreen(self):
        ''' Next button was clicked. '''
        self.ui.tabWidget.setCurrentIndex(1)

    def setupScreen(self, uiobject):
        ''' Sets up the GUI defaults. '''
        uiobject.termLine.setCursorPosition(2)
        uiobject.currentProgress.setValue(0)
        uiobject.sendStop.setDisabled(True)
        uiobject.clearButton.setDisabled(True)
        uiobject.sendOne.setDisabled(True)
        uiobject.sendCont.setDisabled(True)
        uiobject.origwid = self.size().width()
        uiobject.orighit = self.size().height()
        uiobject.label.setPixmap(QtGui.QPixmap(self.directory+'title_grblfeedr.png'))
        uiobject.label_2.setPixmap(QtGui.QPixmap(self.directory+'title_grblfeedr.png'))
        uiobject.comboBox.addItems(self.common_scanPorts())
        uiobject.comboBox_2.setEditable(False)
        baudRates = ["600", "1200", "1800", "2400", "4800", "9600", "19200", "38400", "57600", "115200"]
        uiobject.comboBox_2.addItems(baudRates)
        uiobject.comboBox_2.setCurrentIndex(5)
        uiobject.tab.setDisabled(True)
        uiobject.tab_4.setDisabled(True)
        uiobject.tabWidget.setCurrentIndex(0)
        self.setWindowIcon(QtGui.QIcon(self.directory+'icon_grblfeedr.png'))
        uiobject.termWindow.setHtml("")
        uiobject.termWindow_2.setHtml("")
        res = QtGui.QDesktopWidget().screenGeometry()
        self.move((res.width() / 2) - (self.frameSize().width() / 2), (res.height() / 2) - (self.frameSize().height() / 2))
        
if __name__ == "__main__":
    ''' Starts the application '''
    app = QtGui.QApplication(sys.argv)
    grblapp = GrblForm()
    grblapp.show()
    app.exec_()
    grblapp.common_exitAll()
    sys.exit()
