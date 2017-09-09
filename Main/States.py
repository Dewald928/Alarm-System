#!/usr/bin/env python

from random import randint
from time import clock


##===============================================
## TRANSITIONS

class Transition(object):
    """ Code executed when transitioning from one state to another """

    def __init__(self, tostate):
        self.toState = tostate

    def Execute(self):
        print("Transitioning...")


##===============================================
## STATES

class State(object):
    ''' The base template state which all others will inherit from  '''

    def __init__(self, FSM):
        self.FSM = FSM
        self.timer = 0
        self.startTime = 0

    def Enter(self):
        self.timer = randint(0, 5)
        self.startTime = int(clock())

    def Execute(self):
        pass

    def Exit(self):
        pass


class CleanDishes(State):
    ''' Cleaning the dishes state '''

    def __init__(self, FSM):
        super(CleanDishes, self).__init__(FSM)

    def Enter(self):
        print("Preparing to clean dishes.")
        super(CleanDishes, self).Enter()

    def Execute(self):
        print("Cleaning dishes")
        if (self.startTime + self.timer <= clock()):
            if not (randint(1, 3) % 2):
                self.FSM.ToTransition("toVacuum")
            else:
                self.FSM.ToTransition("toSleep")

    def Exit(self):
        print("Finished cleaning dishes.")


class Vacuum(State):
    ''' State for vacuuming '''

    def __init__(self, FSM):
        super(Vacuum, self).__init__(FSM)

    def Enter(self):
        print("Starting to Vacuum")
        super(Vacuum, self).Enter()

    def Execute(self):
        print("Vacuuming")
        if (self.startTime + self.timer <= clock()):
            if not (randint(1, 3) % 2):
                self.FSM.ToTransition("toSleep")
            else:
                self.FSM.ToTransition("toCleanDishes")

    def Exit(self):
        print("Finished Vacuuming")


class Sleep(State):
    ''' State for Sleeping. Even robots get tired sometimes. :) '''

    def __init__(self, FSM):
        super(Sleep, self).__init__(FSM)

    def Enter(self):
        print("Starting to Sleep")
        super(Sleep, self).Enter()

    def Execute(self):
        print("Sleeping")
        if (self.startTime + self.timer <= clock()):
            if not (randint(1, 3) % 2):
                self.FSM.ToTransition("toVacuum")
            else:
                self.FSM.ToTransition("toCleanDishes")

    def Exit(self):
        print("Waking up from Sleep")