#!/usr/bin/env python

import logging
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


import os, sys
try:
    from PySide import QtCore, QtGui, QtUiTools
except ImportError:
    print "Could not load PySide (Qt) librairies, exiting."
    sys.exit(1)

try:
    from configobj import ConfigObj
except ImportError:
    print "Could not load ConfigObj, exiting."
    sys.exit(1)

from gui.mainwindow import Ui_MainWindow
from gui.choicetable import ChoiceTable
from libmicoach.user import miCoachUser
from libmicoach.errors import *
from config import config, ConfigUI

class AsioUser(QtCore.QThread, miCoachUser):
    """Qt-threaded extension of miCoachUser
    
    Allows running tasks (e.g. downloading workouts) in the background
    while doing something else (e.g. GUI).
    Tasks are launched with do* methods (doLogin, doGetLog, doDownload)
    and warn when finished with Qt signals (LoginFinished, etc.).
    """
    
    LoginAction, GetLogAction, DownloadAction = range(3)
    
    loginFinished = QtCore.Signal(bool)
    getLogFinished = QtCore.Signal(bool)
    downloadFileFinished = QtCore.Signal(int)
    downloadAllFinished = QtCore.Signal(bool)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        miCoachUser.__init__(self)
        
        self.workoutList = None
        self.workouts = None

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
            self.workouts = []
            for id in self.args:
                self.workouts.append(self.getSchedule().getWorkout(id))
                self.downloadFileFinished.emit(id)
    
            self.downloadAllFinished.emit(True)

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
        self.username = username
        
        self.csvFolder = os.path.split(config['data']['csv_path'])[0].format(username=self.username)
        self.xmlFolder = os.path.split(config['data']['xml_path'])[0].format(username=self.username)
        
        self.checkFolder()
    
    def checkFolder(self):
        if config['data'].as_bool('save_csv') and not os.path.exists(self.csvFolder):
            os.makedirs(self.csvFolder)
        
        if config['data'].as_bool('save_xml') and not os.path.exists(self.xmlFolder):
                os.makedirs(self.xmlFolder)
    
    def compareWorkoutList(self, woList):
        """returns ids of workout *not* present in storage folder
        
        Resolves with XML files if save_xml enabled, CSV files otherwise.
        Comparison is made by checking file names with settings.csv|xml_path
        
        @todo: replace comparison with workoutList.__sub__() <= implement woList by folder
        """

        # build arrays of workouts names
        if config['data'].as_bool('save_xml'):
            targetPath = os.path.split(config['data']['xml_path'])[-1]
            targetFolder = self.xmlFolder
        else:
            targetPath = os.path.split(config['data']['csv_path'])[-1]
            targetFolder = self.csvFolder
            
        argList = [(w['id'], targetPath.format(username=self.username, id=w['id'], date=w['date'], name=w['name'])) for w in woList]
        folderList = os.listdir(targetFolder)
        
        return [id for id, name in argList if name not in folderList]
        
        
    def addWorkout(self, workout, check_exists=False):
        if config['data'].as_bool('save_csv'):
            workout.writeCsv(config['data']['csv_path'].format(username=self.username, id=workout.id, date=workout.date, name=workout.name),
                             config['data']['csv_format'])

        if config['data'].as_bool('save_xml'):
            workout.writeXml(config['data']['xml_path'].format(username=self.username, id=workout.id, date=workout.date, name=workout.name))

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
        self.ui.configButton.clicked.connect(self.showConfig)
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
        if config['user'].as_bool('auto_connect'):
            self.processAndGoNext()
    
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

    def downloadFileFinished(self, id):
        self.alreadyDownloaded.append(id)
        log.info("Already downloaded: %s" % str(self.alreadyDownloaded))
        
        self.updateInterface(self.currentView)
    
    def downloadAllFinished(self, workouts):
        if len(self.user.workouts):
            log.info("All workouts downloaded (%d)" % len(self.user.workouts))

            self.ui.progressLabel.setText("All files downloaded, saving")
            
            i = 0
            for w in self.user.workouts:
                i += 1
                self.storage.addWorkout(w)

                # counting from download achieved (e.g. 70%)
                self.ui.progressBar.setValue(self.ProgressBarDownloadRatio + self.ProgressBarSaveRatio*(i/len(self.user.workouts)))

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
            # populate
            try:
                self.ui.emailLine.setText(config['user']['email'])
                self.ui.passwordLine.setText(config['user']['password'])
                self.ui.connectBox.setChecked(config['user'].as_bool('auto_connect'))
            except:
                pass
            
            # buttons
            self.ui.cancelButton.setVisible(False)
            self.ui.previousButton.setVisible(False)
            self.ui.emailLine.setFocus()
            
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
                existing = self.storage.compareWorkoutList(self.user.workoutList)
                
                self.ui.chooseInstructionsIcon.setShown(False)
                self.ui.chooseInstructionsLabel.setText("Found %d workouts (%d new)" % (len(self.user.workoutList), len(existing)))
                self.resize(1000, 450)
                self.centerInterface()
                
                for workout in self.user.workoutList:
                    self.table.addLine(workout, workout['id'] in existing)
                
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

    def showConfig(self):
        conf = ConfigUI(config)
        conf.exec_()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)  

    win  = MainWindow()
    win.show()

    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
                app, QtCore.SLOT("quit()"))
    sys.exit(app.exec_())

