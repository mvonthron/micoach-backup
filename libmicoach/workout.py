
from libmicoach.custompysimplesoap.simplexml import *


class Workout(object):
    def __init__(self, content):
        pass
        #~ if isinstance(content, SimpleXMLElement):
            #~ self.xml = content
        #~ else:
            #~ self.xml = None
            #~ 
        #~ self.id = self.xml.WorkoutId
        #~ self.name = self.xml.Name
        #~ self.date = StartDate
        

    
class WorkoutList(object):
    
    def __init__(self, data):
        self.content = []
        
        # try from xml WorkoutLog
        try:
            for w in data.WorkoutLog:
                self.content.append({'id': int(w.WorkoutId), 
                                     'name': str(w.Name), 
                                     'date': w.StartDate, 
                                     'activity': str(w.ActivityType), 
                                     'type': str(w.CompletedWorkoutType)})
        except AttributeError as e:
            print e.strerror
        # try from array of dict values [{id, name, date}, {}]
    
        # try from folder
        
    def __sub__(self, other):
        """difference between two workout lists"""
        pass
        # [i for i in a + b if i not in a or i not in b]
        
    
    def fromFolder(self, folder):
        try:
            pass
            #~ data = folder.list()
        except:
            pass

    
