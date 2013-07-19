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
        out.add_attribute("xmlns", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
        out.add_attribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        out.add_attribute("xsi:schemaLocation", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")

        out.add_child("Courses")
        course = out.Courses.add_child("Course")

        #
        # HEADERS
        #
        course.add_child("Name", unicode(self.xml.WorkoutName))

        lap = course.add_child("Lap")
        # Total
        lap.add_child("TotalTimeSeconds", self.xml.TotalTime)
        lap.add_child("DistanceMeters", self.xml.TotalDistance.Value)

        # Activity type
        try:
            activity = self.xml.ExerciseType
            if activity.startswith("CoolDown"):
                lap.add_child("Intensity", "Resting")
            else:
                lap.add_child("Intensity", "Active")
        except AttributeError:
            lap.add_child("Intensity", "Active")

        # HR
        avgHr = lap.add_child("AverageHeartRateBpm")
        avgHr.add_attribute("xsi:type", "HeartRateInBeatsPerMinute_t")
        avgHr.add_child("Value", self.xml.AvgHR.Value)
        maxHr = lap.add_child("MaximumHeartRateBpm")
        maxHr.add_attribute("xsi:type", "HeartRateInBeatsPerMinute_t")
        maxHr.add_child("Value", self.xml.PeakHR.Value)

        # GPS
        try:
            beg = self.xml.WorkoutRoute.UserRouteCoordinate[0]
            end = self.xml.WorkoutRoute.UserRouteCoordinate[-1]
            begLat, begLong = beg.Latitude, beg.Longitude
            endLat, endLong = end.Latitude, end.Longitude
        except AttributeError:
            begLat, begLong = 0, 0
            endLat, endLong = 0, 0

        begin = lap.add_child("BeginPosition")
        begin.add_child("LatitudeDegrees", begLat)
        begin.add_child("LongitudeDegrees", begLong)

        end = lap.add_child("EndPosition")
        end.add_child("LatitudeDegrees", endLat)
        end.add_child("LongitudeDegrees", endLong)

        #
        # POINTS
        #
        track = course.add_child("Track")
        #non ISO for now
        d = str(self.xml.StartDateTime).split('.')
        start = datetime.datetime.strptime(d[0], "%Y-%m-%dT%H:%M:%S")

        for point in self.xml.CompletedWorkoutDataPoints.CompletedWorkoutDataPoint:
            trackpoint = track.add_child("Trackpoint")

            delta = timedelta(0, float(point.TimeFromStart))
            
            trackpoint.add_child("Time", (start+delta).isoformat())
            
            trackpoint.add_child("DistanceMeters", point.Distance)
            hr = trackpoint.add_child("HeartRateBpm")
            hr.add_attribute("xsi:type", "HeartRateInBeatsPerMinute_t")
            hr.add_child("Value", point.HeartRate)
            # sensorstate ???
            
            # GPS
            try:
                lat = point.Latitude
                long = point.Longitude
            except AttributeError:
                lat, long = 0, 0
                
            try:
                alt = point.Altitude
            except AttributeError:
                lat = 0

            trackpoint.add_child("Position")
            trackpoint.Position.add_child("LatitudeDegrees", lat)
            trackpoint.Position.add_child("LongitudeDegrees", long)
            trackpoint.add_child("AltitudeMeters", alt)
            
            # Missing : pace, striderate, timefromstart
            # Extensions
            calories = trackpoint.add_child("Extensions").add_child("FatCalories")
            calories.add_attribute("xmlns", "http://www.garmin.com/xmlschemas/FatCalories/v1")
            calories.add_child("Value", point.Calories)
            
            cadence = trackpoint.Extensions.add_child("ActivityTrackpointExtension")
            cadence.add_attribute("xmlns", "http://www.garmin.com/xmlschemas/ActivityExtension/v1")
            cadence.add_attribute("SourceSensor", "Footpod")
            cadence.add_child("RunCadence", point.StrideRate)

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

    
