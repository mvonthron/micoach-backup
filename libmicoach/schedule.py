from libmicoach.services import *
from libmicoach.workout import *


class Schedule(object):
    def __init__(self):
        self.workouts = CompletedWorkout()
    
    def getWorkoutList(self):
        log = self.workouts.GetWorkoutLog(**{})
        
        for w in log.WorkoutLog:
            print w.FormattedStartDate, "-", w.Name, w.ActivityType, w.CompletedWorkoutType
            
        return WorkoutList(log)

    def getLatestWorkout(self):
        print Workout(self.workouts.GetLatestCompletedWorkout(**{}))
