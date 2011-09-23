import sys, time, serial
from PySide import QtCore, QtGui

from outp import Ui_MainWindow
from gcodeformat import GForm

class Worker(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
       
    def run(self):
        while not self.exiting:
            time.sleep(0.01)
            if(oksig[0] == True):
                oksig[0] = False
                self.emit(QtCore.SIGNAL("doney()"))
            
class SerialProcessor(QtCore.QThread):
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        
    def processchunk(self, currentline):
        popped = []
        while ("\n" in currentline) or ("\r" in currentline):
            currentpop = currentline.pop(0)
            popped.extend(currentpop)
        else:
            if(popped):
                popped.pop()
                if(len(popped) > 1):
                    if("".join(popped) == "ok"):
                        oksig[0] = True
                        #print("got okay!")
                        termWindowList.append("<font color=lime><i>["+("".join(popped))+"]</i></font>")
                    else:
                        termWindowList.append("<font color=yellow>["+("".join(popped))+"]</font>")
                    self.emit(QtCore.SIGNAL("regen()"))    
                popped = []
        return ""
    
    def run(self):
        a = 0
        ser.flushInput()
        currentline = []
        while not self.exiting:
            time.sleep(0.01)
            a += 1
            if(True):
                #print("processing chunk serial "+repr(a))
                self.processchunk(currentline)
                chunked = ser.readline()
                if(chunked):
                    currentline.extend(list(chunked.decode('utf-8')))
            
class SetUp(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self)
        
    def setupDefaults(self, parent=None):
        self.termLine.setCursorPosition(2)
        self.currentProgress.setValue(0)
        self.senderThread = Worker()
        self.sendStop.setDisabled(True)
        self.clearButton.setDisabled(True)
        self.sendOne.setDisabled(True)
        self.sendCont.setDisabled(True)
        parent.resize(500, 305)
        self.termWindow.setHtml("")
        self.serialThread = SerialProcessor()
        self.serialThread.start()
        
    def clearInput(self, parent=None):
        if(self.termLine.text() == "Enter Command"):
            self.termLine.clear()
            
    def hitEnter(self, parent=None):
        termWindowList.append("<font color=lime>"+self.termLine.text()+"</font>")
        ser.write((self.termLine.text()+"\n").encode('utf-8'))
        self.regenTerminalWindow()
        self.termLine.clear()

    def openFile(self, parent=None):
        fileName = QtGui.QFileDialog.getOpenFileName(None, u"Select G-Code to send to CNC",u"",u"GCode Files (*.nc *.gc);;All Files (*.*)")
        fLoad = open(fileName[0],'r')
        del(contents[:])
        del(formattedcontents[:])
        self.clearButton.setDisabled(False)
        self.sendOne.setDisabled(False)
        self.sendCont.setDisabled(False)
        outerdisplay.resize(760, 305)
        for line in fLoad:
            contents.append(line)
            lined = line+"<br>"
            formattedcontents.append(lined)
        fLoad.close()
        self.origlength = len(contents)
        self.regenContentWindow()
        
    def click_sendOne(self, parent=None):
        currentliner = contents.pop(0)
        del(formattedcontents[0:3])
        currentline[0] += 1.0
        self.regenContentWindow()
        termWindowList.append("<font color=red>"+currentliner+"</font>")
        ser.writeTimeout = 0.5
        try:
            ser.write((currentliner).encode('utf-8'))
        except:
            termWindowList.append("<font color=yellow>"+"Message was not sent, timeout error."+"</font>")
        self.regenTerminalWindow()
        
    def click_sendCont(self, parent=None):
        self.senderThread.start()
        self.sendStop.setDisabled(False)
        self.sendCont.setDisabled(True)
        self.sendOne.setDisabled(False)
        self.loadButton.setDisabled(True)
        
    def com_threadSender(self, parent=None):
        try:
            currentliner = contents.pop(0)
            del(formattedcontents[0:3])
            currentline[0] += 1.0
            self.regenContentWindow()
            termWindowList.append("<font color=blue>"+currentliner+"</font>")
            ser.write(currentliner.encode('utf-8'))
            self.regenTerminalWindow()
        except:
            self.senderThread.terminate()
          
    def click_clearQueue(self, parent=None):
        del(contents[:])
        del(formattedcontents[:])
        self.sendCont.setDisabled(True)
        self.sendOne.setDisabled(True)
        self.clearButton.setDisabled(True)
        self.origlength = 1
        self.regenContentWindow()
        termWindowList.append("<font color=yellow>"+"-> queue cleared..."+"</font>")
        self.regenTerminalWindow()
        self.currentProgress.setValue((0))

    def click_clearTerm(self, parent=None):
        del(termWindowList[:])
        self.regenTerminalWindow()

    def com_stopCont(self, parent=None):
        termWindowList.append("<font color=yellow>"+"-> stopping..."+"</font>")
        self.regenTerminalWindow()
        self.sendStop.setDisabled(True)
        self.sendCont.setDisabled(False)
        self.sendOne.setDisabled(False)
        self.loadButton.setDisabled(False)
        
    def click_sendStop(self, parent=None):
        self.senderThread.terminate()
        
    def exitAll(self, parent=None):
            pass
            sys.exit()

    def click_actionConnect(self, parent=None):
        pass

    def term_serialThread(self, parent=None):
        pass

    def regenContentWindow(self, parent=None): 
        try:
            if(formattedcontents[1]):
                formattedcontents.insert(1,"</font><font color=grey>")
                formattedcontents.insert(0,"<font color=red size=4><b>>> </font><font color=blue size=4>")
                formattedcontents.append("</font>")
        except:
            pass
            #formattedcontents.append("Queue Empty")
        self.textEdit.setHtml("".join(formattedcontents[0:30]))
        self.currentProgress.setValue((currentline[0]/self.origlength)*100)

    def regenTerminalWindow(self, parent=None):   
        self.termWindow.setHtml("<br>".join(termWindowList[-13:]))

    def setupSlots(self, parent=None):
        QtCore.QObject.connect(self.exitButton, QtCore.SIGNAL("clicked()"), self.exitAll)
        QtCore.QObject.connect(self.loadButton, QtCore.SIGNAL("clicked()"), self.openFile)
        QtCore.QObject.connect(self.actionLoad_GCode, QtCore.SIGNAL("activated()"), self.openFile)
        QtCore.QObject.connect(self.sendOne, QtCore.SIGNAL("clicked()"), self.click_sendOne)
        QtCore.QObject.connect(self.sendCont, QtCore.SIGNAL("clicked()"), self.click_sendCont)
        QtCore.QObject.connect(self.sendStop, QtCore.SIGNAL("clicked()"), self.click_sendStop)
        QtCore.QObject.connect(self.termLine, QtCore.SIGNAL("cursorPositionChanged(int,int)"), self.clearInput)
        QtCore.QObject.connect(self.termLine, QtCore.SIGNAL("returnPressed()"), self.hitEnter)
        QtCore.QObject.connect(self.senderThread, QtCore.SIGNAL("terminated()"), self.com_stopCont)
        QtCore.QObject.connect(self.senderThread, QtCore.SIGNAL("doney()"), self.com_threadSender)
        QtCore.QObject.connect(self.clearButton, QtCore.SIGNAL("clicked()"), self.click_clearQueue)
        QtCore.QObject.connect(self.clearTerm, QtCore.SIGNAL("clicked()"), self.click_clearTerm)
        QtCore.QObject.connect(self.actionConnect, QtCore.SIGNAL("activated()"), self.click_actionConnect)
        QtCore.QObject.connect(self.serialThread, QtCore.SIGNAL("terminated()"), self.term_serialThread)
        QtCore.QObject.connect(self.serialThread, QtCore.SIGNAL("regen()"), self.regenTerminalWindow)

contents = []
termWindowList =  []
formattedcontents = []
continueRunning = []
oksig = [1]
origlength = 0
currentline = [0]
Formatter = GForm()
ser = serial.Serial('COM10',9600,8,'N',1,0.01)
app = QtGui.QApplication(sys.argv)
outerdisplay = QtGui.QMainWindow()
window = SetUp(app)
window.setupUi(outerdisplay)
window.setupDefaults(outerdisplay)
window.setupSlots(outerdisplay)

outerdisplay.show()
sys.exit(app.exec_())