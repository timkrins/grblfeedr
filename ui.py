import sys
from PySide import QtCore, QtGui

from outp import Ui_MainWindow
from gcodeformat import GForm

class SetUp(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self)
        
        
    def clearInput(self):
        if(self.termLine.text() == "Enter Command"):
            self.termLine.clear()
            
    def hitEnter(self):
        print(self.termLine.text())
        self.termLine.clear()

    def openFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(None, u"Select G-Code to send to CNC",u"",u"GCode Files (*.nc *.gc);;All Files (*.*)")
        #print(fileName[0])
        fLoad = open(fileName[0],'r')
        for line in fLoad:
            contents.append(line)
            lined = Formatter.format_html(line)
            formattedcontents.append(lined)
        fLoad.close()
        self.textEdit.setHtml("".join(formattedcontents))
        
    def setupSlots(self, parent=None):
        QtCore.QObject.connect(self.exitButton, QtCore.SIGNAL("clicked()"), sys.exit)
        QtCore.QObject.connect(self.loadButton, QtCore.SIGNAL("clicked()"), self.openFile)
        self.termLine.setCursorPosition(2)
        QtCore.QObject.connect(self.termLine, QtCore.SIGNAL("cursorPositionChanged(int,int)"), self.clearInput)
        QtCore.QObject.connect(self.termLine, QtCore.SIGNAL("returnPressed()"), self.hitEnter)


#QLineEdit.focusInEvent (self, QFocusEvent)

def main():

    app = QtGui.QApplication(sys.argv)
    outerdisplay = QtGui.QMainWindow()
    window = SetUp(app)
    window.setupUi(outerdisplay)
    window.setupSlots(outerdisplay)
    outerdisplay.show()
    sys.exit(app.exec_())

contents = []
formattedcontents = []
Formatter = GForm()

if __name__ == '__main__':
    main()