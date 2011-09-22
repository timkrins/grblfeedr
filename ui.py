import sys
from PySide import QtCore, QtGui

from outp import Ui_MainWindow
from gcodeformat import GForm

class MyHighlighter( QtGui.QSyntaxHighlighter ):
    def __init__( self, parent ):
      QtGui.QSyntaxHighlighter.__init__( self, parent )
      self.parent = parent
      self.highlightingRules = []

      keyword = QtGui.QTextCharFormat()
      keyword.setForeground( QtCore.Qt.darkBlue )
      keyword.setFontWeight( QtGui.QFont.Bold )
      keywords = [ "x", "X", "for", "if", "in",
                                "next", "repeat", "return", "switch",
                                "try", "while" ]
      for word in keywords:
        pattern = QtCore.QRegExp(word)
        rule = HighlightingRule( pattern, keyword )
        self.highlightingRules.append( rule )
        
    def highlightBlock( self, text ):
      for rule in self.highlightingRules:
        expression = QtCore.QRegExp( rule.pattern )
        index = expression.indexIn( text )
        while index >= 0:
          length = expression.matchedLength()
          self.setFormat( index, length, rule.format )
          index = text.indexOf( expression, index + length )
      self.setCurrentBlockState( 0 )

        
class HighlightingRule():
  def __init__( self, pattern, format ):
    self.pattern = pattern
    self.format = format
    
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
            lined = line+"<br>"
            formattedcontents.append(lined)
        fLoad.close()
        highlighter = MyHighlighter( self.textEdit )
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