#!/usr/bin/env python
import logging
logging.basicConfig(level=logging.INFO)

import os, sys
from PySide import QtCore, QtGui, QtUiTools

from gui.mainwindow import Ui_MainWindow
from libmicoach.user import miCoachUser

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.user = None
        
        self.ui.connectButton.clicked.connect(self.connectUser)
        
    def connectUser(self):
        email  = self.ui.emailLine.text()
        passwd = self.ui.passwordLine.text()
        
        if not email or not passwd:
            QtGui.QMessageBox.critical(self, "miCoach backup", "Email and/or password missing")
        else:
            self.ui.statusLine.setText("Connecting miCoach user")
            try:
                self.user = miCoachUser(email, passwd)
                self.ui.statusLine.setText("Connected (%s)" % self.user.screenName)
            except:
                QtGui.QMessageBox.critical(self, "miCoach backup", "Login failed")
                
            
    

if __name__ == '__main__':  
    app = QtGui.QApplication(sys.argv)  

    win  = MainWindow()
    win.show()

    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    sys.exit(app.exec_())

