from datetime import datetime

from libmicoach.simplexml import *

class Workout(object):
    def __init__(self, content):
        
        if isinstance(content, SimpleXMLElement):
            self.xml = content

            try:
                self.id = self.xml.CompletedWorkoutID
            except AttributeError:
                try:
                    self.id = self.xml.WorkoutID
                except:
                    pass

            self.date = datetime.datetime.strptime(str(self.xml.StartDateTime), "%Y-%m-%dT%H:%M:%S")
            self.name = self.xml.WorkoutName

        else:
            self.xml = None
            

        
    def writeCsv(self, filename, formatstring="{time}; {hr}; {calories}; {pace};"):
        format = lambda p: formatstring.format(time=p.TimeFromStart, intervalno=p.IntervalOrderNumber, 
                                                   distance=p.Distance, hr=p.HeartRate,
                                                   calories=p.Calories, pace=p.Pace,
                                                   rate=p.StrideRate, steps=p.Steps,
                                                   longitude=p.Longitude, latitude=p.Latitude,
                                                   altitude=p.Altitude
                                                   )
        
        lines = [format(point) for point in self.xml.CompletedWorkoutDataPoint]
        
        file = open(filename, "w")
        file.write("\n".join(lines))
        file.close()
    
    def writeXml(self, filename):
        file = open(filename, "w")
        file.write(self.xml.as_xml())
        file.close()
    
class WorkoutList(object):
    
    def __init__(self, data):
        self.content = []
        
        # try with SimpleXmlElement from WorkoutLog
        try:
            for w in data.WorkoutLog:
                start = datetime.datetime.strptime(str(w.StartDate), "%Y-%m-%dT%H:%M:%S")
                end   = datetime.datetime.strptime(str(w.StopDate), "%Y-%m-%dT%H:%M:%S")

                d = int(w.Distance.Value)
                if d > 1000:
                    distance = "%.1f km" % (d/1000.)
                else:
                    distance = "%d m" % d
                
                self.content.append({'id': int(w.WorkoutId), 
                                     'name': str(w.Name), 
                                     'date': str(start), 
                                     'activity': str(w.ActivityType), 
                                     'type': str(w.CompletedWorkoutType),
                                     'time': str(end-start),
                                     'distance': distance,
                                     'hr': int(w.AvgHR.Value),
                                     'pace': float(w.AvgPace.Value)
                                     })
        except:
            pass

        # try from array of dict values [{id, name, date}, {}]
    
        # try from folder
    
    def __len__(self):
        return len(self.content)
    
    def __iter__(self):
        for line in self.content:
            yield line
    
    def __sub__(self, other):
        """difference between two workout lists"""
        pass
        # [i for i in a + b if i not in a or i not in b]
    
    def __repr__(self):
        return "WorkoutList: contains (%d) workouts" % len(self.content)
        
    def display(self):
        for entry in self.content:
            print "%8d\t%-20s\t%10s\t%-5s\t%-8s\t%8s\t%s\t%d\t%.2f" % (entry['id'], entry['name'], entry['date'], 
                                                        entry['activity'], entry['type'], entry['time'],
                                                        entry['distance'], entry['hr'], entry['pace'])
    
    def fromFolder(self, folder):
        try:
            pass
            #~ data = folder.list()
        except:
            pass

    