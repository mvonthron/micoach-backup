import logging
log = logging.getLogger(__name__)

import os
from config import config

class Storage(object):
    def __init__(self, username):
        self.username = username
        
        self.csvFolder = os.path.split(config['data']['csv_path'])[0].format(username=self.username)
        self.xmlFolder = os.path.split(config['data']['xml_path'])[0].format(username=self.username)
        self.tcxFolder = os.path.split(config['data']['tcx_path'])[0].format(username=self.username)
        
        self.checkFolder()
    
    def checkFolder(self):
        if config['data'].as_bool('save_csv') and not os.path.exists(self.csvFolder):
            os.makedirs(self.csvFolder)
        
        if config['data'].as_bool('save_xml') and not os.path.exists(self.xmlFolder):
                os.makedirs(self.xmlFolder)
        
        if config['data'].as_bool('save_tcx') and not os.path.exists(self.tcxFolder):
                os.makedirs(self.tcxFolder)
    
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
            
        argList = [(w['id'], targetPath.format(username=self.username, id=w['id'], date=w['date'].replace(":", "-"), name=w['name'])) for w in woList]
        folderList = os.listdir(targetFolder)
        
        return [id for id, name in argList if name not in folderList]
        
        
    def addWorkout(self, workout, check_exists=False):
        if config['data'].as_bool('save_csv'):
            workout.writeCsv(config['data']['csv_path'].format(username=self.username, id=workout.id, date=workout.date.strftime("%Y-%m-%d %H-%M-%S"), name=workout.name),
                             config['data']['csv_format'])

        if config['data'].as_bool('save_xml'):
            workout.writeXml(config['data']['xml_path'].format(username=self.username, id=workout.id, date=workout.date.strftime("%Y-%m-%d %H-%M-%S"), name=workout.name))
        
        if config['data'].as_bool('save_tcx'):
            workout.writeTcx(config['data']['tcx_path'].format(username=self.username, id=workout.id, date=workout.date.strftime("%Y-%m-%d %H-%M-%S"), name=workout.name))
        
