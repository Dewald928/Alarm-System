#!/usr/bin/env python

from random import randint
from time import clock


# ===============================================
# TRANSITIONS

class Transition(object):
    ''' Code executed when transitioning from one state to another '''

    def __init__(self, toState):
        self.toState = toState

    def Execute(self):
        print("Transitioning...")


# ===============================================
# STATES

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


class Disarmed(State):
    ''' Disarmed state '''

    def __init__(self, FSM):
        super(Disarmed, self).__init__(FSM)

    def Enter(self):
        print("Preparing to Disarm.")
        super(Disarmed, self).Enter()

    def Execute(self):
        print("Disarmed")
        if (self.startTime + self.timer <= clock()):
            if not (randint(1, 3) % 2):
                self.FSM.ToTransition("toVacuum")
            else:
                self.FSM.ToTransition("toSleep")

    def Exit(self):
        print("Finished cleaning dishes.")


class Armed(State):
    ''' Disarmed state '''

    def __init__(self, FSM):
        super(Armed, self).__init__(FSM)

    def Enter(self):
        print("Preparing to Arm.")
        super(Armed, self).Enter()

    def Execute(self):
        print("Armed")
        if (self.startTime + self.timer <= clock()):
            if not (randint(1, 3) % 2):
                self.FSM.ToTransition("toVacuum")
            else:
                self.FSM.ToTransition("toSleep")

    def Exit(self):
        print("Finished cleaning dishes.")