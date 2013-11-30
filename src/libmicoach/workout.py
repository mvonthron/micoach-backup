from datetime import datetime, timedelta

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

            d = str(self.xml.StartDateTime).split('.')
            self.date = datetime.datetime.strptime(d[0], "%Y-%m-%dT%H:%M:%S")
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
        
        with open(filename, "w") as f:
            f.write("\n".join(lines))
    
    def writeXml(self, filename):
        with open(filename, "w") as f:
            f.write(self.xml.as_xml())
        
    def writeTcx(self, filename):
        # Write Garmin's TCX file
        out = SimpleXMLElement("<TrainingCenterDatabase />")
        out.add_attribute("xsi:schemaLocation", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")
        out.add_attribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        out.add_attribute("xmlns", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
        out.add_attribute("xmlns:ns2", "http://www.garmin.com/xmlschemas/ActivityExtension/v2")

        activity = out.add_child("Activities").add_child("Activity")
        try:
            if str(self.xml.ActivityType) == "Run":
                activity.add_attribute("Sport", "Running")
        except:
            pass
        
        activity.add_child("Id", self.xml.CompletedWorkoutID)
        lap = activity.add_child("Lap")
        
        # StartTime attribute
        d = str(self.xml.StartDateTimeUTC).split('.')[0] # '.' separate from unsupported microseconds
        start = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")
        lap.add_attribute("StartTime", start.strftime("%Y-%m-%dT%H:%M:%SZ"))
        
        lap.add_child("DistanceMeters", self.xml.TotalDistance.Value)
        # Total
        lap.add_child("TotalTimeSeconds", self.xml.TotalTime)
        lap.add_child("DistanceMeters", self.xml.TotalDistance.Value)
        if self.xml.TotalCalories:
            lap.add_child("Calories", self.xml.TotalCalories.Value)
        
        # Exercise type
        try:
            activity = self.xml.ExerciseType
            if activity.startswith("CoolDown"):
                lap.add_child("Intensity", "Resting")
            else:
                lap.add_child("Intensity", "Active")
        except AttributeError:
            lap.add_child("Intensity", "Active")
        
        # has HR values?
        if self.xml.AvgHR.Value and int(self.xml.AvgHR.Value) > 0:
            hasHR = True
        else:
            hasHR = False
        
        if hasHR:
            lap.add_child("AverageHeartRateBpm").add_child("Value", self.xml.AvgHR.Value)
            lap.add_child("MaximumHeartRateBpm").add_child("Value", self.xml.PeakHR.Value)
        
        track = lap.add_child("Track")
        for point in self.xml.CompletedWorkoutDataPoints.CompletedWorkoutDataPoint:
            trackpoint = track.add_child("Trackpoint")
            
            delta = timedelta(0, float(point.TimeFromStart))
            trackpoint.add_child("Time", (start+delta).strftime("%Y-%m-%dT%H:%M:%SZ"))
            
            # GPS
            try:
                lat = point.Latitude
                long = point.Longitude
            except AttributeError:
                pass
            else:
                trackpoint.add_child("Position")
                trackpoint.Position.add_child("LatitudeDegrees", lat)
                trackpoint.Position.add_child("LongitudeDegrees", long)
            
            try:
                alt = point.Altitude
            except AttributeError:
                pass
            else:
                trackpoint.add_child("AltitudeMeters", alt)
            
            trackpoint.add_child("DistanceMeters", point.Distance)
            if hasHR:
                trackpoint.add_child("HeartRateBpm").add_child("Value", point.HeartRate)

            # Extensions
            if point.Calories or point.StrideRate:
                trackpoint.add_child("Extensions")
                
            if point.Calories and int(point.Calories) > 0:
                calories = trackpoint.Extensions.add_child("FatCalories")
                calories.add_attribute("xmlns", "http://www.garmin.com/xmlschemas/FatCalories/v1")
                calories.add_child("Value", point.Calories)
            
            if point.StrideRate and int(point.StrideRate) > 0:
                cadence = trackpoint.Extensions.add_child("TPX")
                cadence.add_attribute("xmlns", "http://www.garmin.com/xmlschemas/ActivityExtension/v2")
                cadence.add_attribute("SourceSensor", "Footpod")
                cadence.add_child("RunCadence", point.StrideRate)
                
        # Write
        with open(filename, 'w') as f:
            f.write(out.as_xml(pretty=True))
    
class WorkoutList(object):
    
    def __init__(self, data):
        self.content = []
        
        # try with SimpleXmlElement from WorkoutLog
        try:
            for w in data.WorkoutLog:
                try: 
                    # splitting date to handle microsec
                    d = str(w.StartDate).split('.')
                    start = datetime.datetime.strptime(d[0], "%Y-%m-%dT%H:%M:%S")
                    d = str(w.StopDate).split('.')
                    end   = datetime.datetime.strptime(d[0], "%Y-%m-%dT%H:%M:%S")

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

    
