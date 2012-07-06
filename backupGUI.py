#!/usr/bin/env python

import logging
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


import os, sys
from PySide import QtCore, QtGui, QtUiTools

from gui.mainwindow import Ui_MainWindow
from gui.choicetable import ChoiceTable
from libmicoach.user import miCoachUser
from libmicoach.errors import *
from libmicoach import settings

class AsioUser(QtCore.QThread, miCoachUser):
    LoginAction, GetLogAction, DownloadAction = range(3)
    
    loginFinished = QtCore.Signal(bool)
    getLogFinished = QtCore.Signal(bool)
    downloadFileFinished = QtCore.Signal(int)
    downloadAllFinished = QtCore.Signal(object)

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
            
        elif self.action == self.DownloadAction:
            workouts = []
            for id in self.args:
                workouts.append(self.getSchedule().getWorkout(id))
                self.downloadFileFinished.emit(id)
    
            self.downloadAllFinished.emit(workouts)

    # calls
    def doLogin(self, email, passwd):
        self.args = (email, passwd)
        self.action = self.LoginAction
        self.start()
    
    def doGetLog(self):
        self.args = None
        self.action = self.GetLogAction
        self.start()
        
    def doDownload(self, ids):
        log.info("About to download ids %s", str(ids))
        self.args = ids
        self.action = self.DownloadAction
        self.start()
    

class Storage(object):
    def __init__(self, username):
        if settings.use_user_folder:
            userFolder = "%s/" % username
        else:
            userFolder = ""
            
        self.csvPath = "%s/%s/" % (settings.root_folder, userFolder)
        self.xmlPath = "%s/%s/xml" % (settings.root_folder, userFolder)
        
        self.checkFolder()
    
    def checkFolder(self):
        if not os.path.exists(self.csvPath):
            os.makedirs(self.csvPath)
        
        if settings.save_raw_xml:
            if not os.path.exists(self.xmlPath):
                os.makedirs(self.xmlPath)
    
    def addWorkout(self, workout, check_exists=False):
        if settings.save_raw_xml:
            filename = "%s/%s - %s.xml" % (self.xmlPath, workout.date, workout.name)
            workout.writeXml(filename)


class MainWindow(QtGui.QMainWindow):
    ConnectView, ChooseView, DownloadView = range(3)
    ProgressBarDownloadRatio = 70
    ProgressBarSaveRatio = 100 - ProgressBarDownloadRatio
    
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.table = ChoiceTable(self.ui.choosePage)
        self.ui.chooseVLayout.addWidget(self.table)
        
        # connections
        self.ui.nextButton.clicked.connect(self.processAndGoNext)
        self.ui.previousButton.clicked.connect(self.abortAndGoPrevious)
        
        self.user = AsioUser(self)
        self.user.loginFinished.connect(self.loginFinished)
        self.user.getLogFinished.connect(self.getLogFinished)
        self.user.downloadFileFinished.connect(self.downloadFileFinished)
        self.user.downloadAllFinished.connect(self.downloadAllFinished)
        
        self.storage = None
        
        self.toBeDownloaded = []
        self.alreadyDownloaded = []
        
        self.updateInterface(self.ConnectView)

    
    def loginFinished(self, success):
        if success:
            self.user.doGetLog()
            self.goNext()
        else:
            QtGui.QMessageBox.critical(self, "miCoach backup", "Login failed")
            self.updateInterface(self.ConnectView)
    
    def getLogFinished(self, success):
        if success:
            self.storage = Storage(self.user.screenName)
            self.updateInterface(self.ChooseView)
        else:
            QtGui.QMessageBox.critical(self, "miCoach backup", "Could not retrieve workout list")
            #~ self.updateInterface(self.ChooseView)

    def downloadFileFinished(self, id):
        self.alreadyDownloaded.append(id)
        log.info("Already downloaded: %s" % str(self.alreadyDownloaded))
        
        self.updateInterface(self.currentView)
    
    def downloadAllFinished(self, workouts):
        if len(workouts):
            log.info("All workouts downloaded (%d)" % len(workouts))

            self.ui.progressLabel.setText("All files downloaded, saving")
            
            i = 0
            for w in workouts:
                i += 1
                #~ w.writeXml("data/%s/xml/%s - %s.xml" % (self.user.screenName, w.date, w.name))
                self.storage.addWorkout(w)

                # counting from download achieved (e.g. 70%)
                self.ui.progressBar.setValue(self.ProgressBarDownloadRatio + self.ProgressBarSaveRatio*(i/len(workouts)))

            log.info("All workouts written")
            self.ui.progressLabel.setText("All files saved")
            

    
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
            self.toBeDownloaded = self.table.getCheckedId()
            self.alreadyDownloaded = []
            
            if not len(self.toBeDownloaded):
                QtGui.QMessageBox.critical(self, "miCoach backup", "No workout selected")
            else:
                self.user.doDownload(self.toBeDownloaded)
                self.goNext()

        # DownloadView
        elif self.currentView == self.DownloadView:
            log.info("Bye")
            # exiting
            if self.user.isRunning():
                self.user.terminate()
            QtCore.QCoreApplication.instance().quit()
        
    def abortAndGoPrevious(self):
        if self.user.isRunning():
            self.user.terminate()
        
        # ConnectView
        if self.currentView == self.ConnectView:
            self.user.logout()
        
        # ChooseView
        elif self.currentView == self.ChooseView:
            self.user.workoutList = None
            
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
        
    def centerInterface(self):
        geo = self.frameGeometry()
        center = QtGui.QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())
        
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
            self.resize(480, 205)
            self.centerInterface()
        
        # ChooseView
        elif self.currentView == self.ChooseView:
            # buttons
            self.ui.cancelButton.setVisible(True)
            self.ui.previousButton.setVisible(True)
            self.ui.nextButton.setText("Next")

            if not self.user.workoutList:
                self.ui.chooseInstructionsIcon.setShown(True)
                self.ui.chooseInstructionsLabel.setText("Loading list of workouts")
            else:
                self.ui.chooseInstructionsIcon.setShown(False)
                self.ui.chooseInstructionsLabel.setText("Found %d workouts" % len(self.user.workoutList))
                self.resize(1000, 450)
                self.centerInterface()
                
                for workout in self.user.workoutList:
                    self.table.addLine(workout)
                
                        
        # DownloadView
        elif self.currentView == self.DownloadView:
            # buttons
            self.ui.cancelButton.setVisible(True)
            self.ui.previousButton.setVisible(True)
            self.ui.nextButton.setText("Finish")
            
            # progress
            self.ui.progressBar.setValue(self.ProgressBarDownloadRatio*len(self.alreadyDownloaded)/len(self.toBeDownloaded))
            if len(self.alreadyDownloaded) < len(self.toBeDownloaded):
                self.ui.progressLabel.setText("Downloading file %d of %d" % (len(self.alreadyDownloaded)+1, len(self.toBeDownloaded)))
            else:
                self.ui.progressLabel.setText("All files downloaded")
            
            self.resize(480, 205)
            self.centerInterface()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)  

    win  = MainWindow()
    win.show()

    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    sys.exit(app.exec_())

