import sys, time, serial
from PySide import QtCore, QtGui

from outp import Ui_MainWindow

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
                
    def __del__(self, parent=None):
        self.exiting = True
        self.wait()
            
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
                    popnstrip = "".join(popped).strip()
                    if(popnstrip == "ok"):
                        oksig[0] = True
                        #print("got okay!")
                        termWindowList.append("<font color=lime><i>["+(popnstrip)+"]</i></font>")
                    else:
                        termWindowList.append("<font color=yellow>["+(popnstrip)+"]</font>")
                    self.emit(QtCore.SIGNAL("regen()"))    
                popped = []
        return ""
    
    def run(self):
        a = 0
        window.ser.flushInput()
        currentline = []
        while not self.exiting:
            time.sleep(0.01)
            a += 1
            if(not self.exiting):
                #print("processing chunk serial "+repr(a))
                self.processchunk(currentline)
                try:
                    chunked = window.ser.readline()
                    if(chunked):
                        currentline.extend(list(chunked.decode('utf-8')))
                except:
                    print('this is a strange error, possibly caused by the serial being deleted before the thread')
                    
    def __del__(self, parent=None):
        self.exiting = True
        self.wait()
        
class SetUp(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self)
 
    def centerOnScreen (self, parent=None):
        res = QtGui.QDesktopWidget().screenGeometry()
        parent.move((res.width() / 2) - (parent.frameSize().width() / 2), (res.height() / 2) - (parent.frameSize().height() / 2))

    def setupDefaults(self, parent=None):
        self.termLine.setCursorPosition(2)
        self.currentProgress.setValue(0)
        self.senderThread = Worker()
        self.sendStop.setDisabled(True)
        self.clearButton.setDisabled(True)
        self.sendOne.setDisabled(True)
        self.sendCont.setDisabled(True)
        self.origwid = parent.size().width()
        self.orighit = parent.size().height()
        self.label.setPixmap(QtGui.QPixmap("grblfeeder.png"))
        self.label_2.setPixmap(QtGui.QPixmap("grblfeeder.png"))
        self.comboBox.addItems(self.com_scan())
        self.comboBox_2.setEditable(False)
        self.comboBox_2.addItems(["600", "1200", "1800", "2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self.comboBox_2.setCurrentIndex(5)
        self.tab.setDisabled(True)
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("grblico.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.termWindow.setHtml("")
        self.serialThread = SerialProcessor()
        
    def clearInput(self, parent=None):
        if(self.termLine.text() == "Enter Command"):
            self.termLine.clear()
            
    def hitEnter(self, parent=None):
        termWindowList.append("<font color=lime>"+self.termLine.text()+"</font>")
        window.ser.writeTimeout = 0.5
        try:
            window.ser.write((self.termLine.text()+"\n").encode('utf-8'))
        except:
            termWindowList.append("<font color=yellow>"+"Message was not sent, timeout error."+"</font>")
        self.regenTerminalWindow()
        self.termLine.clear()

    def openFile(self, parent=None):
        try:
            fileName = QtGui.QFileDialog.getOpenFileName(None, u"Select G-Code to send to CNC",u"",u"GCode Files (*.nc *.gc *.ngc);;All Files (*.*)")
            fLoad = open(fileName[0],'r')
            del(contents[:])
            del(formattedcontents[:])
            self.clearButton.setDisabled(False)
            self.sendOne.setDisabled(False)
            self.sendCont.setDisabled(False)
            #outerdisplay.resize(760, self.orighit)
            for line in fLoad:
                contents.append(line)
                lined = line+"<br>"
                formattedcontents.append(lined)
            fLoad.close()
            self.origlength = len(contents)
            self.regenContentWindow()
        except:
            print('file not opened correctly')
        
    def click_sendOne(self, parent=None):
        currentliner = contents.pop(0)
        del(formattedcontents[0:3])
        currentline[0] += 1.0
        self.regenContentWindow()
        termWindowList.append("<font color=red>"+currentliner+"</font>")
        window.ser.writeTimeout = 0.5
        try:
            window.ser.write((currentliner).encode('utf-8'))
        except:
            termWindowList.append("<font color=yellow>"+"Message was not sent, timeout error."+"</font>")
        self.regenTerminalWindow()
        
    def click_sendCont(self, parent=None):
        try:
            if(window.ser):
                self.senderThread.start()
                self.sendStop.setDisabled(False)
                self.sendCont.setDisabled(True)
                self.sendOne.setDisabled(False)
                self.loadButton.setDisabled(True)
            else:
                self.tabWidget.setCurrentIndex(0)
        except:
            self.tabWidget.setCurrentIndex(0)
            
    def com_threadSender(self, parent=None):
        try:
            currentliner = contents.pop(0)
            del(formattedcontents[0:3])
            currentline[0] += 1.0
            self.regenContentWindow()
            termWindowList.append("<font color=blue>"+currentliner+"</font>")
            window.ser.writeTimeout = 0.5
            try:
                window.ser.write(currentliner.encode('utf-8'))
            except:
                termWindowList.append("<font color=yellow>"+"Message was not sent, timeout error."+"</font>")
                #self.click_sendStop()
                
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
        QtCore.QObject.connect(self.exitButton2, QtCore.SIGNAL("clicked()"), self.exitAll)
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
        QtCore.QObject.connect(self.connectButton, QtCore.SIGNAL("clicked()"), self.click_connectButton) 
        QtCore.QObject.connect(self.disconnectButton, QtCore.SIGNAL("clicked()"), self.click_disconnectButton) 
        QtCore.QObject.connect(self.nextScreen, QtCore.SIGNAL("clicked()"), self.click_nextScreen) 
    
    def buildlist_incmac(self):
        if(sys.platform == "darwin"):
            devs = os.listdir("/dev/")
            devs = [filename for filename in devs if filename[0] == 'c']
            devs = [filename for filename in devs if filename[1] == 'u']
            devs = ["/dev/"+filename for filename in devs]
            return devs
        else:
            return range(256)
        
    def com_scan(self):
        coms = []
        for porty in self.buildlist_incmac():
            try:
                s = serial.Serial(porty)
                coms.append( str(s.portstr))
                s.close()
            except serial.SerialException:
                pass
        return coms    
         
    def click_connectButton(self, parent=None):
        try:
            self.ser = serial.Serial(port=self.comboBox.currentText(), baudrate=self.comboBox_2.currentText())
            self.connectButton.setText("Connected.")
            self.connectButton.setDisabled(True)
            self.disconnectButton.setDisabled(False)
            self.comboBox.setDisabled(True)
            self.comboBox_2.setDisabled(True)
            self.tab.setDisabled(False)
            self.serialThread.start()
        except:
            print('error connecting')
            
    def click_disconnectButton(self, parent=None):
        try:
            self.serialThread.terminate()
            self.ser.close()
            self.connectButton.setText("Connect")
            self.connectButton.setDisabled(False)
            self.comboBox.setDisabled(False)
            self.comboBox_2.setDisabled(False)
            self.tab.setDisabled(True)
            self.disconnectButton.setDisabled(True)
            
        except:
            print('error disconnecting')
            
    def click_nextScreen(self, parent=None):
        self.tabWidget.setCurrentIndex(1)

contents = []
termWindowList =  []
formattedcontents = []
continueRunning = []
oksig = [1]
origlength = 0
currentline = [0]

# my objects are all over the place - I never actually bothered to sketch out their relationships...

app = QtGui.QApplication(sys.argv)
outerdisplay = QtGui.QMainWindow()
window = SetUp(app)
window.setupUi(outerdisplay)
window.setupDefaults(outerdisplay)
window.setupSlots(outerdisplay)
window.centerOnScreen(outerdisplay)
outerdisplay.show()
app.exec_()
#sys.exit()