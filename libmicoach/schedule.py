from libmicoach.services import *
from libmicoach.workout import *


class Schedule(object):
    def __init__(self):
        self.workouts = CompletedWorkout()
    
    def getWorkoutList(self):
        log = self.workouts.GetWorkoutLog()
        return WorkoutList(log)

    def getLatestWorkout(self):
        w = self.workouts.GetLatestCompletedWorkout()
        return Workout(w)

    def getWorkout(self, id):
        return Workout(self.workouts.GetCompletedWorkoutById(completedWorkoutId=id))
