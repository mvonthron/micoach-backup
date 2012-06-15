import httplib, urllib
import sys
import logging

from libmicoach.custompysimplesoap.client import SoapClient
from libmicoach import settings
from libmicoach.errors import *

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class miCoachService(object):
    params = {}
    client = None
    
    def __init__(self, client_location, client_namespace):
        self.client = SoapClient(location = client_location,
                             action = client_namespace,
                             namespace = client_namespace, 
                             soap_ns='soap', trace = settings.trace, exceptions=True)
                             
        if not settings.isconnected is True:
            self.connect()
        self.client.add_http_header("cookie", settings.authcookie) 
    
    def __getattr__(self, attr):
        return lambda self=self, *args, **kwargs: self.call(attr,*args,**kwargs)
            
    def call(self, method, *args, **kwargs):
        if not self.client is None:
            return self.client.call(method, *args, **kwargs)
            
    def connect(self):
        log.info("Initializing connection")
        
        params = urllib.urlencode({'password':settings.password, 'email':settings.email, 'TimeZoneInfo': settings.timezoneinfo})
        headers ={"Content-type": "application/x-www-form-urlencoded",
                  "Connection": "keep-alive",
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                 }
        conn = httplib.HTTPSConnection("www.adidas.com", 443)
        conn.request("POST", "/ca/micoach/login.aspx", params, headers)

        response = conn.getresponse()
        http_authcookie = response.getheader('set-cookie')
        
        loginClient = SoapClient(location = "http://www.micoach.com/v2.0/Services/UserProfileWS.asmx",
                                action = 'http://adidas.com/micoach/v4/',
                                namespace = "http://adidas.com/micoach/v4", 
                                soap_ns='soap', trace = settings.trace, exceptions=True)
        loginClient.add_http_header("Cookie", http_authcookie)
        
        sys.stdout.flush()
        headers, response = loginClient.Login(return_http_headers=True, **{'email': settings.email, 'password': settings.password})
        
        if str(response.ResultStatusMessage) == "SUCCESS":
            log.info("Login successful: (%s)", response.ScreenName)
            settings.authcookie =  loginClient.response['set-cookie']
            settings.isconnected = True
        else:
            log.info("Login failed: %s", response.ResultStatusMessage)
            raise LoginFailed()
            


class CompletedWorkout(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "http://www.micoach.com/v2.0/Services/CompletedWorkoutWS.asmx", 
                                      "http://adidas.com/micoach/v4/")

class UserProfile(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "http://www.micoach.com/v2.0/Services/UserProfileWS.asmx", 
                                      "http://adidas.com/micoach/v4/")

class SyncAPI(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "http://www.micoach.com/v2.0/Services/SyncAPIWS.asmx", 
                                      "http://adidas.com/micoach/v3/")

class Calendar(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "http://www.micoach.com/v2.0/Services/CalendarWS.asmx", 
                                      "http://adidas.com/micoach/v3/")

class Route(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "http://www.micoach.com/v2.0/Services/RouteWS.asmx", 
                                      "http://adidas.com/micoach/v3/")

class Activity(miCoachService):
    def __init__(self):
        miCoachService.__init__(self, "http://www.micoach.com/v2.0/Services/ActivityWS.asmx", 
                                      "http://adidas.com/micoach/v4/")
