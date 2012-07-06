import httplib, urllib
import sys
import logging
log = logging.getLogger(__name__)

from libmicoach import settings
from libmicoach.errors import *
from libmicoach.simplexml import *

class miCoachService(object):
    def __init__(self, service):
        self.location = ("/v2.0/Services/%s") % service
        self.http = httplib.HTTPConnection("www.micoach.com")

        if not settings.isconnected:
            self.connect()
    
    def __getattr__(self, attr):
        return lambda self=self, *args, **kwargs: self.call(attr,*args,**kwargs)

    def call(self, method, *args, **kwargs):
        if settings.isconnected:
            try:
                data = self.GET(method, **kwargs)
                return SimpleXMLElement(data)
            except Exception as e:
                print e.strerror

    
    def GET(self, action, *args, **kwargs):
        params = urllib.urlencode(kwargs)
        log.debug("GET %s/%s?%s" % (self.location, action, params))
        
        self.http.request("GET", ("%s/%s?%s") % (self.location, action, params), headers={'cookie': settings.authcookie})
        data = self.http.getresponse().read()
        return data
    
    def POST(self, action, *args, **kwargs):
        pass
    
    def connect(self):
        log.info("Initializing connection")
        
        params = urllib.urlencode({'password':settings.password, 'email':settings.email, 'TimeZoneInfo': settings.timezoneinfo})
        headers ={"Content-type": "application/x-www-form-urlencoded",
                  "Connection": "keep-alive",
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                 }
        https = httplib.HTTPSConnection("www.adidas.com", 443)
        https.request("POST", "/ca/micoach/login.aspx", params, headers)
        http_authcookie = https.getresponse().getheader('set-cookie')
        
        params = urllib.urlencode({'password':settings.password, 'email':settings.email})
        self.http.request("GET", "/v2.0/Services/UserProfileWs.asmx/Login?"+params, headers={'cookie':http_authcookie})
        response = self.http.getresponse()
        xml = SimpleXMLElement(text=response.read())

        if str(xml.ResultStatusMessage) == "SUCCESS":
            log.info("Login successful: (%s)", xml.ScreenName)
            settings.authcookie =  response.getheader('set-cookie')
            settings.isconnected = True
        else:
            log.warning("Login failed: %s", xml.ResultStatusMessage)
            raise LoginFailed()

class CompletedWorkout(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "CompletedWorkoutWS.asmx")

class UserProfile(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "UserProfileWS.asmx")

class SyncAPI(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "SyncAPIWS.asmx")

class Calendar(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "CalendarWS.asmx")

class Route(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "RouteWS.asmx")

class Activity(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "ActivityWS.asmx")
