
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
                                     'type': str(w.CompletedWorkoutType),
                                     'time': -1,
                                     'distance': int(w.Distance.Value),
                                     'hr': int(w.AvgHR.Value),
                                     'pace': float(w.AvgPace.Value)
                                     })
        except AttributeError as e:
            print e.strerror
        # try from array of dict values [{id, name, date}, {}]
    
        # try from folder
        
    def __len__(self):
        return len(self.content)
    
    def __sub__(self, other):
        """difference between two workout lists"""
        pass
        # [i for i in a + b if i not in a or i not in b]
    
    def __repr__(self):
        return "WorkoutList: contains (%d) workouts" % len(self.content)
        
    def display(self):
        
        for entry in self.content:
            print "%8d\t%-20s\t%10s\t%-5s\t%-8s\t%8s\t%d\t%d\t%.2f" % (entry['id'], entry['name'], entry['date'], 
                                                        entry['activity'], entry['type'], entry['time'],
                                                        entry['distance'], entry['hr'], entry['pace'])
    
    def fromFolder(self, folder):
        try:
            pass
            #~ data = folder.list()
        except:
            pass

    
