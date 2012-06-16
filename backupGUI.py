#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.INFO)

import os, sys
from PySide import QtCore, QtGui, QtUiTools

from gui.mainwindow import Ui_MainWindow
from libmicoach.user import miCoachUser
from libmicoach.errors import *

# looks ugly
class AsioUser(QtCore.QThread, miCoachUser):
    LoginAction, GetLogAction = range(2)
    loginFinished = QtCore.Signal(bool)
    getLogFinished = QtCore.Signal(bool)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        miCoachUser.__init__(self)
        
        self.workoutList = None

    def run(self):
        if self.action == self.LoginAction:
            email, passwd = self.args
            try:
                self.login(email, passwd)
            except LoginFailed:
                self.loginFinished.emit(False)
            else:
                self.loginFinished.emit(True)
                
        elif self.action == self.GetLogAction:
            self.workoutList = self.getSchedule().getWorkoutList()
            self.getLogFinished.emit(True)
    
    def doLogin(self, email, passwd):
        self.args = (email, passwd)
        self.action = self.LoginAction
        self.start()
    
    def doGetLog(self):
        self.args = None
        self.action = self.GetLogAction
        self.start()
    

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

        self.user = AsioUser(self)
        self.user.loginFinished.connect(self.loginFinished)
        self.user.getLogFinished.connect(self.getLogFinished)
    
    def loginFinished(self, success):
        if success:
            self.user.doGetLog()
            self.goNext()
        else:
            QtGui.QMessageBox.critical(self, "miCoach backup", "Login failed")
            self.updateInterface(self.ConnectView)
    
    def getLogFinished(self, success):
        if success:
            self.updateInterface(self.ChooseView)
        else:
            QtGui.QMessageBox.critical(self, "miCoach backup", "Could not retrieve workout list")
            #~ self.updateInterface(self.ChooseView)
            
    def processAndGoNext(self):
        # ConnectView
        if self.currentView == self.ConnectView:
            email  = self.ui.emailLine.text()
            passwd = self.ui.passwordLine.text()
            if not email or not passwd:
                QtGui.QMessageBox.critical(self, "miCoach backup", "Email and/or password missing")
                return
        
            self.user.doLogin(email, passwd)

            self.ui.loadingIcon.setVisible(True)
            self.ui.loadingLabel.setVisible(True)

        # ChooseView
        elif self.currentView == self.ChooseView:
            pass
            
        # DownloadView
        elif self.currentView == self.DownloadView:
            pass
        
    def abortAndGoPrevious(self):
        if self.user.isRunning():
            self.user.terminate()
        
        # ConnectView
        if self.currentView == self.ConnectView:
            self.user.logout()
        
        # ChooseView
        elif self.currentView == self.ChooseView:
            pass
            
        # DownloadView
        elif self.currentView == self.DownloadView:
            pass
        
        self.goPrevious()
    
    def goNext(self):
        self.updateInterface(self.currentView+1)
        
    def goPrevious(self):
        self.updateInterface(self.currentView-1)
    
    
    def cancel(self):
        pass 
        
    def updateInterface(self, view):
        if not view in (self.ConnectView, self.ChooseView, self.DownloadView):
            return
        
        self.currentView = view
        self.ui.viewPages.setCurrentIndex(self.currentView)
        
        self.ui.loadingIcon.setVisible(False)
        self.ui.loadingLabel.setVisible(False)
        
        # ConnectView
        if self.currentView == self.ConnectView:
            # buttons
            self.ui.cancelButton.setVisible(False)
            self.ui.previousButton.setVisible(False)
            self.ui.nextButton.setText("Next")
        
        # ChooseView
        elif self.currentView == self.ChooseView:
            # buttons
            self.ui.cancelButton.setVisible(True)
            self.ui.previousButton.setVisible(True)
            self.ui.nextButton.setText("Next")

            if not self.user.workoutList:
                self.ui.chooseInstructionsLabel.setText("Loading list of workouts")
            else:
                self.ui.chooseInstructionsLabel.setText("Found %d workouts" % len(self.user.workoutList))
                
            
        # DownloadView
        elif self.currentView == self.DownloadView:
            # buttons
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

