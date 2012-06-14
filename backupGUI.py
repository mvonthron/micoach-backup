#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.INFO)

import os, sys
from PySide import QtCore, QtGui, QtUiTools

from gui.mainwindow import Ui_MainWindow
from libmicoach.user import miCoachUser

class MainWindow(QtGui.QMainWindow):
    ConnectView, ChooseView, DownloadView = range(3)
    
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # connections
        self.ui.nextButton.clicked.connect(self.processAndGoNext)
        self.ui.previousButton.clicked.connect(self.abortAndGoPrevious)
        
        self.updateInterface(self.ConnectView)

    def processAndGoNext(self):
        self.updateInterface(self.currentView+1)
    
    def abortAndGoPrevious(self):
        self.updateInterface(self.currentView-1)
    
    def cancel(self):
        pass 
        
    def updateInterface(self, view):
        if not view in (self.ConnectView, self.ChooseView, self.DownloadView):
            return
        
        self.currentView = view
        self.ui.viewPages.setCurrentIndex(self.currentView)
        
        # ConnectView
        if self.currentView == self.ConnectView:
            self.ui.cancelButton.setVisible(False)
            self.ui.previousButton.setVisible(False)
            self.ui.nextButton.setText("Next")
        
        # ChooseView
        elif self.currentView == self.ChooseView:
            self.ui.cancelButton.setVisible(True)
            self.ui.previousButton.setVisible(True)
            self.ui.nextButton.setText("Next")

            
        # DownloadView
        elif self.currentView == self.DownloadView:
            self.ui.cancelButton.setVisible(True)
            self.ui.previousButton.setVisible(True)
            self.ui.nextButton.setText("Finish")

    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)  

    win  = MainWindow()
    win.show()

    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    sys.exit(app.exec_())

