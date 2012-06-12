import logging

from libmicoach import settings
from libmicoach.services import UserProfile

log = logging.getLogger(__name__)

class miCoachUser(object):
    
    
    def __init__(self, email, password):
        
        #~ if settings.debug:
        log.info('Started')
        log.debug('Started')
        log.warn('Started')
        
        settings.email = email
        settings.password = password
        
        self.service = UserProfile()
        
        self.getInfos()

    def getInfos(self):
        infos = self.service.GetUserInfo(**{})
        
        self.screenName = str(infos.ScreenName)
        #~ self.firstName = str(infos.FirstName)
        #~ self.lastName = str(infos.LastName)
        self.email = str(infos.Email)
        
    def disconnect(self):
        pass
        
    def testConnection(self):
        pass
            
    def getWorkoutsList(self):
        pass
        
    def getLatestWorkout(self):
        pass

    def getSchedule(self):
        pass
    
    
