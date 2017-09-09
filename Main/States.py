#!/usr/bin/env python

from random import randint
from time import clock
from time import sleep
from gpiozero import Buzzer
from pad4pi import rpi_gpio

buzzer = Buzzer(26)

# ===============================================
# TRANSITIONS

class Transition(object):
    """ Code executed when transitioning from one state to another """

    def __init__(self, tostate):
        self.toState = tostate

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
    ''' Disarming State '''
    a = True #for Active in this state

    def __init__(self, FSM):
        super(Disarmed, self).__init__(FSM)

    def Enter(self):
        print("Starting to Disarm")
        super(Disarmed, self).Enter()

    def Execute(self):
        self.KeypadInitialize()
        print("Disarmed")
        while True:
            if self.a == False:
                self.FSM.ToTransition("toArmed")
                break

    def Exit(self):
        print("Exiting Disarmed")

    def KeypadInitialize(self):
        factory = rpi_gpio.KeypadFactory()
        keypad = factory.create_4_by_3_keypad()  # makes assumptions about keypad layout and GPIO pin numbers
        keypad.registerKeyPressHandler(self.key_pressed)

    def key_pressed(self, key):
        try:
            print(key)
            int_key = int(key)
            if int_key >= 0 and int_key <= 9:
                # digit_entered(key)
                buzzer.on()
                sleep(0.1)
                buzzer.off()
        except ValueError:
            self.non_digit_entered(key)
            buzzer.on()
            sleep(0.05)
            buzzer.off()
            sleep(0.05)
            buzzer.on()
            sleep(0.05)
            buzzer.off()

    def non_digit_entered(self, key):
        # global entered_passcode
        # check if all sensors can be activated
        # +++++++++++++++++++++++++++++++++++++
        if key == "*":
            self.a = False

class Armed(State):
    ''' Arming state '''
    a = True

    def __init__(self, FSM):
        super(Armed, self).__init__(FSM)

    def Enter(self):
        print("Preparing to Arm")
        # beep 10 seconds
        for i in range(10):
            startTime = clock()
            timeInterval = 1
            while (startTime + timeInterval > clock()):
                pass
            buzzer.on()
            sleep(0.1)
            buzzer.off()
        buzzer.on()
        sleep(2)
        buzzer.off()
        super(Armed, self).Enter()

    def Execute(self):
        print("Armed")
        while True:
            if self.a == False:
                self.FSM.ToTransition("toArmed")
                break

    def Exit(self):
        print("Exiting Armed")



