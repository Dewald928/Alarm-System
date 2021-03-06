#!/usr/bin/env python

from random import randint
from time import clock
from time import sleep
from pad4pi import rpi_gpio
import lcddriver
import RPi.GPIO as GPIO
import threading
import time

# Networking ###########################################################################################################
import pycurl
from io import BytesIO
import json
import os

serverURL = 'http://192.168.137.144/ServerJSONThreadModel.php' #PHP Server address (local host using XAMPP)

#Buffer
buffer = []
bufferEmpty = True
alarmID = '255' #Alarm Unit registration number

#File IO
logFilename = "TriggerLog.txt"

#Delays
delay_IFS = 0.1
delay_backoff = 1


class sendThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.alive = False

    def run(self):
        global buffer
        global bufferEmpty
        # Define States
        IDLE = 1
        SEND = 2
        DISCONNECTED = 3

        currentState = IDLE
        response = [False, ""]
        k = 0
        while self.alive:
            time.sleep(delay_IFS)
            if currentState == IDLE:
                if not bufferEmpty:
                    currentState = SEND
                    response = transmit()
                    k = 0
            if currentState == SEND:
                if (response[0] == True) and (bufferEmpty):
                    currentState = IDLE
                if (response[0] == True) and (not bufferEmpty):
                    response = transmit()
                    k = 0
                if response[0] == False:
                    response = transmit()
                    k = k + 1
                if k >= 3:
                    display.clear()
                    display.display_string("Offline", 1)
                    display.display_string("Error: " + str(response[1]), 2)
                    #print("LCD Output:\nOffline\nError: " + str(response[1]))
                    response = transmit()
                    currentState = DISCONNECTED
            if currentState == DISCONNECTED:
                time.sleep(delay_backoff)
                if response[0] == True:
                    currentState = IDLE
                    display.clear()
                    display.display_string("Reconnected", 1)
                if response[0] == False:
                    response = transmit()

def transmit():
    """Transmit the following tuple to server:
    (AlarmID,Timestamp1,Timestamp2...)"""
    global buffer
    global bufferEmpty
    try:
        threadLock.acquire()
        post_data = {'alarmID': alarmID, 'timestamps': buffer}

        jsonEncoder = json.JSONEncoder()
        recieveBuffer = BytesIO()  # Captures reply from Server
        c = pycurl.Curl()  # Create Curl Object
        c.setopt(c.URL, serverURL)
        c.setopt(c.POSTFIELDS, jsonEncoder.encode(post_data))
        c.setopt(c.WRITEDATA, recieveBuffer)

        c.perform()  # Make transfer and recieve URL information
        c.close()
        if os.path.isfile(logFilename):
            os.remove(logFilename)
        body = recieveBuffer.getvalue()
        print(body.decode('iso-8859-1'))  # Decode bytes to string
        buffer = []
        bufferEmpty = True
        threadLock.release()
        return [True, ""]
    except pycurl.error as e:
        c.close()

        with open(logFilename, 'w') as f:
            json.dump(buffer, f)

        try:
            threadLock.release()
        except:
            pass

        return [False, str(e.args[0])]

def alertServer():
    global buffer, bufferEmpty
    threadLock.acquire()
    buffer.append(str(int(time.time())))
    bufferEmpty = False
    threadLock.release()

    time.sleep(10)

def killTransmitThread():
    transmitThread.alive = False
    transmitThread.join()

#Load unsent messages to buffer
if os.path.isfile(logFilename):
    try:
        with open(logFilename, 'r') as f:
            buffer = json.load(f)
    except:
        os.remove(logFilename)

#Initialize Threading
threadLock = threading.Lock()
transmitThread = sendThread()
transmitThread.alive = True
transmitThread.start()
########################################################################################################################

#Hardware
#########
GPIO.setmode(GPIO.BCM)
write_lock = threading.Lock()

# Buzzer
buzzer = 26
GPIO.setup(buzzer, GPIO.OUT)
GPIO.output(buzzer, 0)

# PIR sensors
PIR = [8, 24, 25, 7]
GPIO.setup(PIR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Door sensors
DOOR = [20, 21]
GPIO.setup(DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Triggered Pin
triggered_pin = 0

# LCD Display
display = lcddriver.lcd()
display.backlight_off()

# Keypad
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_4_by_3_keypad()  # makes assumptions about keypad layout and GPIO pin numbers

# Passwords
entered_passcode = ""
correct_passcode = "1234"
psw_entries = 3

# ++++++= Create pin out file++++++++++



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
    active = True  # for Active in this state

    def __init__(self, FSM):
        super(Disarmed, self).__init__(FSM)

    def Enter(self):
        print("Starting to Disarm")
        super(Disarmed, self).Enter()

    def Execute(self):
        keypad.registerKeyPressHandler(self.key_pressed)

        display.clear()
        display.display_string("System Disarmed", 1)
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
                singleBeep()
        except ValueError:
            self.non_digit_entered(key)
            doubleBeep()

    def non_digit_entered(self, key):
        # global entered_passcode
        # check if all sensors can be activated
        # +++++++++++++++++++++++++++++++++++++
        if key == "*":
            if GPIO.input(DOOR[0]) or GPIO.input(DOOR[1]):
                print("Door opened")
                display.clear()
                display.display_string("Close Doors", 1)
            else:
                print("Door not opened")
                self.active = False



class Armed(State):
    ''' Arming state '''
    triggered = False

    def __init__(self, FSM):
        super(Armed, self).__init__(FSM)

    def MOTION(self, PIR_PIN):
        write_lock.acquire()
        if (self.triggered == False):
            global triggered_pin
            triggered_pin = PIR_PIN
            print("Motion Detected on pin " + str(PIR_PIN))
            display.clear()
            display.display_string(str(PIR_PIN) + "Motion Detected", 2)
            self.triggered = True
        write_lock.release()

    def DOOR_OPEN(self, PIN):
        write_lock.acquire()
        if (self.triggered == False):
            global triggered_pin
            triggered_pin = PIN
            print("Door Contact Open on pin " + str(PIN))
            display.clear()
            display.display_string(str(PIN) + " Door Open", 2)
            self.triggered = True
        write_lock.release()

    def Enter(self):
        print("Preparing to Arm")
        # keypad.unregisterKeyPressHandler(Disarmed.key_pressed)
        display.clear()
        display.display_string("System Arming", 1)
        # beep 10 seconds
        for i in range(10):
            startTime = clock()
            timeInterval = 1
            while (startTime + timeInterval > clock()):
                pass
            singleBeep()
        GPIO.output(buzzer, 1)
        sleep(1)
        GPIO.output(buzzer, 0)
        super(Armed, self).Enter()

    def Execute(self):
        print("Armed")
        display.clear()
        display.display_string("System Armed", 1)

        # PIR sensors signal handler
        for pin in PIR: GPIO.add_event_detect(pin, GPIO.RISING, callback=self.MOTION)
        # Door contact signal handler
        for pin in DOOR: GPIO.add_event_detect(pin, GPIO.RISING, callback=self.DOOR_OPEN, bouncetime=200)

        while True:
            if self.triggered == True:  # if one of the sensors are triggered go to triggered state
                self.FSM.ToTransition("toTriggered")
                break

    def Exit(self):
        print("Exiting Armed")
        self.triggered = False
        # Remove interrupt handlers
        for i in PIR: GPIO.remove_event_detect(i)
        for j in DOOR: GPIO.remove_event_detect(j)


class Triggered(State):
    ''' The triggered state if one of the sensors were tripped '''
    disarm = False
    active = False

    def __init__(self, FSM):
        super(Triggered, self).__init__(FSM)

    def correct_passcode_entered(self):
        print("Passcode accepted. Access granted.")
        self.disarm = True

    def incorrect_passcode_entered(self):
        global psw_entries, entered_passcode
        psw_entries = psw_entries - 1
        entered_passcode = ""
        print("Incorrect passcode. " + str(psw_entries) + " attempts left")
        display.clear()
        display.display_string("Incorrect Code!", 1)
        display.display_string(str(psw_entries) + " Attempts Left", 2)
        if psw_entries <= 0:
            self.active = True

    def digit_entered(self, key):
        global entered_passcode, correct_passcode

        entered_passcode += str(key)
        print(entered_passcode)
        display.clear()
        display.display_string("Enter Passcode:", 1)
        display.display_string(entered_passcode, 2)


        if len(entered_passcode) == len(correct_passcode):
            if entered_passcode == correct_passcode:
                self.correct_passcode_entered()
            else:
                self.incorrect_passcode_entered()

    def non_digit_entered(self, key):
        global entered_passcode

        if key == "*" and len(entered_passcode) > 0:
            entered_passcode = entered_passcode[:-1]
            print(entered_passcode)
            display.clear()
            display.display_string("Enter Passcode:", 1)
            display.display_string(entered_passcode, 2)

    def key_pressed(self, key):
        try:
            int_key = int(key)
            if int_key >= 0 and int_key <= 9:
                self.digit_entered(key)
                singleBeep()
        except ValueError:
            self.non_digit_entered(key)
            doubleBeep()

    def Enter(self):
        print("Entering Triggered")
        keypad.registerKeyPressHandler(self.key_pressed)  # signal handler
        display.clear()
        display.display_string("Enter Password:", 1)

    def Execute(self):
        print("Triggered")
        GPIO.output(buzzer, 1)
        time = 20
        timeout = 0
        while timeout < time:
            sleep(1)
            timeout = timeout + 1
            if self.disarm == True:  # correct password, will disarm device
                GPIO.output(buzzer, 0)
                self.FSM.ToTransition("toDisarmed")
                break
            if self.active == True:  # after 3 wrong password attempt, alarm will go active
                GPIO.output(buzzer, 0)
                self.FSM.ToTransition("toActive")
                break
        if timeout >= time:
            GPIO.output(buzzer, 0)
            self.FSM.ToTransition("toActive")

    def Exit(self):
        global entered_passcode, psw_entries
        print("Exiting Triggered")
        keypad.unregisterKeyPressHandler(self.key_pressed)  # Disable disarmed key handler
        entered_passcode = ""
        psw_entries = 3
        self.disarm = False
        self.active = False
        doubleBeep()
        singleBeep()


class Active(State):
    ''' The Active state if one system timed out without correct code'''
    disarm = False
    arm = False

    def __init__(self, FSM):
        super(Active, self).__init__(FSM)

    def correct_passcode_entered(self):
        print("Passcode accepted. Access granted.")
        self.disarm = True

    def incorrect_passcode_entered(self):
        global psw_entries, entered_passcode
        psw_entries = psw_entries - 1
        entered_passcode = ""
        print("Incorrect passcode. " + str(psw_entries) + " attempts left")
        display.clear()
        display.display_string("Incorrect Code!", 1)
        display.display_string(str(psw_entries) + " Attempts Left", 2)
        if psw_entries <= 0:
            keypad.unregisterKeyPressHandler(self.key_pressed)  # Disable disarmed key handler
            # self.active = True


    def digit_entered(self, key):
        global entered_passcode, correct_passcode

        entered_passcode += str(key)
        print(entered_passcode)
        display.clear()
        display.display_string("Enter Passcode:", 1)
        display.display_string(entered_passcode, 2)

        if len(entered_passcode) == len(correct_passcode):
            if entered_passcode == correct_passcode:
                self.correct_passcode_entered()
            else:
                self.incorrect_passcode_entered()

    def non_digit_entered(self, key):
        global entered_passcode

        if key == "*" and len(entered_passcode) > 0:
            entered_passcode = entered_passcode[:-1]
            print(entered_passcode)
            display.clear()
            display.display_string("Enter Passcode:", 1)
            display.display_string(entered_passcode, 2)

    def key_pressed(self, key):
        try:
            int_key = int(key)
            if int_key >= 0 and int_key <= 9:
                self.digit_entered(key)
                singleBeep()
        except ValueError:
            self.non_digit_entered(key)
            doubleBeep()

    """==========================================================================="""
    def Enter(self):
        print("Entering Active")
        GPIO.output(buzzer, 1)
        keypad.registerKeyPressHandler(self.key_pressed)  # signal handler for alarm disable
        # write the triggered pin to the log
        write_to_log()

    def Execute(self):
        print("Weeee Wooooo Weeeee WOOOO!")
        display.clear()
        display.display_string("Sending Alarm", 1)

        # Sound Alarm

        # Networking +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        alertServer() # Send Alert to Server
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # After correct password entered wil stop
        time = 20  # annoy time
        timeout = 0
        while timeout < time:
            sleep(1)
            timeout = timeout + 1
            if self.disarm == True:  # correct password, will disarm device
                GPIO.output(buzzer, 0)
                self.FSM.ToTransition("toDisarmed")
                break

        # if self.disarm == False:  # timeout will arm device again
        #     self.FSM.ToTransition("toArmed")
        self.FSM.ToTransition("toDisarmed")

    def Exit(self):
        global entered_passcode, psw_entries
        print("Exiting Active")
        keypad.unregisterKeyPressHandler(self.key_pressed)  # Disable disarmed key handler
        entered_passcode = ""
        psw_entries = 3
        self.disarm = False
        GPIO.output(buzzer, 0)


def singleBeep():
    GPIO.output(buzzer, 1)
    sleep(0.1)
    GPIO.output(buzzer, 0)


def doubleBeep():
    GPIO.output(buzzer, 1)
    sleep(0.05)
    GPIO.output(buzzer, 0)
    sleep(0.05)
    GPIO.output(buzzer, 1)
    sleep(0.05)
    GPIO.output(buzzer, 0)


def write_to_log():
    global triggered_pin

    # open file
    file = open("/home/pi/Desktop/logs.txt", "a")
    file.write(str(int(time.time())) + "," + str(triggered_pin) + "\n")

    # close the opened file
    file.close()


