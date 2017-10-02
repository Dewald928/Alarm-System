#!/usr/bin/env python

from random import randint
from time import clock
from time import sleep
from pad4pi import rpi_gpio
import lcddriver
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


# Buzzer
buzzer = 26
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, 0)
# PIR sensors
PIR = [7]
GPIO.setup(PIR, GPIO.IN)

# Door sensors
DOOR = [16, 12]
GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# LCD Display
display = lcddriver.lcd()
# display.lcd_display_string("System Disarmed", 1)
# Keypad
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_4_by_3_keypad()  # makes assumptions about keypad layout and GPIO pin numbers




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
    ''' The base GPIO.output(buzzer, 0)late state which all others will inherit from  '''

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
    active = True #for Active in this state

    def __init__(self, FSM):
        super(Disarmed, self).__init__(FSM)

    def Enter(self):
        print("Starting to Disarm")
        super(Disarmed, self).Enter()

    def Execute(self):
        keypad.registerKeyPressHandler(self.key_pressed)

        display.lcd_display_string("System Disarmed", 1)
        print("Disarmed")

        while True:
            if self.active == False:
                self.FSM.ToTransition("toArmed")
                break

    def Exit(self):
        print("Exiting Disarmed")
        keypad.unregisterKeyPressHandler(self.key_pressed)  # Disable disarmed key handler
        self.active = True


    def key_pressed(self, key):
        try:
            print(key)
            int_key = int(key)
            if int_key >= 0 and int_key <= 9:
                # digit_entered(key)
                GPIO.output(buzzer, 1)
                sleep(0.1)
                GPIO.output(buzzer, 0)
        except ValueError:
            self.non_digit_entered(key)
            GPIO.output(buzzer, 1)
            sleep(0.05)
            GPIO.output(buzzer, 0)
            sleep(0.05)
            GPIO.output(buzzer, 1)
            sleep(0.05)
            GPIO.output(buzzer, 0)

    def non_digit_entered(self, key):
        # global entered_passcode
        # check if all sensors can be activated
        # +++++++++++++++++++++++++++++++++++++
        if key == "*":
            self.active = False


class Armed(State):
    ''' Arming state '''
    triggered = False

    def __init__(self, FSM):
        super(Armed, self).__init__(FSM)

    def MOTION(self, PIR_PIN):
        print("Motion Detected on pin " + str(PIR_PIN))
        display.lcd_display_string(str(PIR_PIN) + "Motion Detected", 2)
        self.triggered = True

    def DOOR_OPEN(self, PIN):
        print("Door Contact Open on pin " + str(PIN))
        display.lcd_display_string(str(PIN) + " Door Open", 2)
        self.triggered = True

    def Enter(self):
        print("Preparing to Arm")
        display.lcd_clear()
        display.lcd_display_string("System Arming", 1)
        # beep 10 seconds
        for i in range(1):
            startTime = clock()
            timeInterval = 1
            while (startTime + timeInterval > clock()):
                pass
            GPIO.output(buzzer, 1)
            sleep(0.1)
            GPIO.output(buzzer, 0)
        GPIO.output(buzzer, 1)
        sleep(2)
        GPIO.output(buzzer, 0)
        super(Armed, self).Enter()

    def Execute(self):
        print("Armed")
        display.lcd_clear()
        display.lcd_display_string("System Armed", 1)

        # PIR sensors signal handler
        for pin in PIR: GPIO.add_event_detect(pin, GPIO.RISING, callback=self.MOTION)
        # Door contact signal handler
        for pin in DOOR: GPIO.add_event_detect(pin, GPIO.RISING, callback=self.DOOR_OPEN)

        while True:
            if self.triggered == True:  # if one of the sensors are triggered go to triggered state
                self.FSM.ToTransition("toTriggered")
                break

    def Exit(self):
        print("Exiting Armed")

        # Remove interrupt handlers
        for i in PIR: GPIO.remove_event_detect(i)
        for j in DOOR: GPIO.remove_event_detect(j)


class Triggered(State):
    ''' The triggered state if one of the sensors were tripped '''

    def __init__(self, FSM):
        super(Triggered, self).__init__(FSM)

    def Enter(self):
        print("Entering Triggered")
        display.lcd_clear()
        display.lcd_display_string("Enter Password:", 1)

    def Execute(self):
        print("Triggered")
        GPIO.output(buzzer, 1)
        timeout = 0
        while timeout < 30:
            sleep(1)
            timeout = timeout + 1
            # +++++++++++++
            # if correct password entered go to disarmed
            # if psw wrong 3 times to to active
        GPIO.output(buzzer, 0)
        self.FSM.ToTransition("toActive")

    def Exit(self):
        print("Exiting Triggered")


class Active(State):
    ''' The Active state if one system timed out without correct code'''


    def __init__(self, FSM):
        super(Active, self).__init__(FSM)

    def Enter(self):
        print("Entering Active")

    def Execute(self):
        print("Weeee Wooooo Weeeee WOOOO!")
        display.lcd_clear()
        display.lcd_display_string("Sending Alarm", 1)

        # Sound Alarm

        sleep(20)

        # ++++++++++++++++++++
        # Send Log to database
        # ++++++++++++++++++++

        # After correct password entered wil stop

        self.FSM.ToTransition("toDisarmed")

    def Exit(self):
        print("Exiting Active")