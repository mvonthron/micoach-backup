import httplib, urllib
import sys
import logging
log = logging.getLogger(__name__)

from libmicoach.errors import *
from libmicoach.simplexml import *

class miCoachService(object):
    isconnected = False
    authcookie = ""
    
    def __init__(self, service, email=None, password=None):
        self.location = ("/Services/%s") % service
        self.http = httplib.HTTPConnection("micoach.adidas.com")
        #httplib.HTTPConnection.debuglevel = 1
        
        if not miCoachService.isconnected:
            if not email or not password:
                raise MissingCredential()
            
            log.info("Not yet connected, connecting.")
            self.connect(email, password)
    
    def __getattr__(self, attr):
        return lambda self=self, *args, **kwargs: self.call(attr,*args,**kwargs)

    def call(self, method, *args, **kwargs):
        if miCoachService.isconnected:
            xml = SimpleXMLElement()
            try:
                data = self.GET(method, **kwargs)
                xml = SimpleXMLElement(data)
            except Exception as e:
                print e.strerror
            
            if int(xml.ResultStatusCode) == 0:
                return xml
            elif int(xml.ResultStatusCode) == 1001:
                raise SessionTimeout()
            elif int(xml.ResultStatusCode) == 1002:
                raise NotAuthenticated()

    
    def GET(self, action, *args, **kwargs):
        params = urllib.urlencode(kwargs)
        log.debug("GET %s/%s?%s" % (self.location, action, params))
        
        self.http.request("GET", ("%s/%s?%s") % (self.location, action, params), headers={'cookie': miCoachService.authcookie})
        data = self.http.getresponse().read()
        return data
    
    def POST(self, action, *args, **kwargs):
        pass
    
    def connect(self, email, password):
        log.info("Initializing connection")
        
        params = urllib.urlencode({'password': password, 'email': email})
        headers ={"Content-type": "application/x-www-form-urlencoded",
                  "Connection": "keep-alive",
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                 }
        https = httplib.HTTPSConnection("www.adidas.com", 443)
        https.request("POST", "/ca/micoach/login.aspx", params, headers)
        http_authcookie = https.getresponse().getheader('set-cookie')
        
        params = urllib.urlencode({'password': password, 'email': email})
        self.http.request("GET", "/Services/UserProfileWs.asmx/Login?"+params)#, headers={'cookie':http_authcookie})
        response = self.http.getresponse()
        xml = SimpleXMLElement(text=response.read())
        
        if str(xml.ResultStatusMessage) == "SUCCESS":
            log.info("Login successful: (%s)", xml.ScreenName)
            miCoachService.authcookie = filter(lambda item: "micoach_authtoken" in item, response.getheader('set-cookie').split())[0]
            miCoachService.isconnected = True
        else:
            log.warning("Login failed: %s", xml.ResultStatusMessage)
            raise LoginFailed()

class CompletedWorkout(miCoachService):
    def __init__(self, email=None, password=None):
        miCoachService.__init__(self, "CompletedWorkoutWS.asmx", email, password)

class UserProfile(miCoachService):
    def __init__(self, email=None, password=None):
        miCoachService.__init__(self, "UserProfileWS.asmx", email, password)

class SyncAPI(miCoachService):
    def __init__(self, email=None, password=None):
        miCoachService.__init__(self, "SyncAPIWS.asmx", email, password)

class Calendar(miCoachService):
    def __init__(self, email=None, password=None):
        miCoachService.__init__(self, "CalendarWS.asmx", email, password)

class Route(miCoachService):
    def __init__(self, email=None, password=None):
        miCoachService.__init__(self, "RouteWS.asmx", email, password)

class Activity(miCoachService):
    def __init__(self, email=None, password=None):
        miCoachService.__init__(self, "ActivityWS.asmx", email, password)

