import logging

log = logging.getLogger(__name__)

from libmicoach import settings
from libmicoach.services import *
from libmicoach.schedule import *
from libmicoach.errors import *

class miCoachUser(object):
    def __init__(self, email=None, password=None):
        log.debug('Starting initializing miCoach user')
        if not email is None and not password is None:
            self.login(email, password)


    def login(self, email, password):
        settings.email = email
        settings.password = password
        
        self.profile = UserProfile()
        self.schedule = Schedule()
        
        self.getProfile()
        
    def getProfile(self):
        log.debug('Retrieving user informations')
        
        profile = self.profile.GetUserProfile()
        self.screenName = str(profile.ScreenName)
        self.email = str(profile.Email)

        
    def logout(self):
        pass
        
    def testConnection(self):
        pass
        
    def getSchedule(self):
        return self.schedule
    
    
