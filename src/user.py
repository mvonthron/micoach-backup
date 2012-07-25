
try:
    from PySide import QtCore, QtGui, QtUiTools
except ImportError:
    print "Could not load PySide (Qt) librairies, exiting."
    sys.exit(1)

from libmicoach.user import miCoachUser
from libmicoach.errors import *



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
