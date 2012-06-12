import logging

log = logging.getLogger(__name__)

from libmicoach import settings
from libmicoach.services import *
from libmicoach.schedule import *

class miCoachUser(object):
    
    
    def __init__(self, email, password):
        
        #~ if settings.debug:
        log.info('Starting initializing miCoach user')
        
        settings.email = email
        settings.password = password
        
        self.profile = UserProfile()
        self.schedule = Schedule()
        
        self.getInfos()

    def getInfos(self):
        log.info('Retrieving user informations')
        
        infos = self.profile.GetUserInfo(**{})
        
        self.screenName = str(infos.ScreenName)
        self.email = str(infos.Email)
        
    def disconnect(self):
        pass
        
    def testConnection(self):
        pass
        
    def getSchedule(self):
        return self.schedule
    
    
