#!/usr/bin/env python

import time
from Alarm_Class import Alarm
from States import killTransmitThread
import RPi.GPIO as GPIO
import lcddriver

display = lcddriver.lcd()

try:

    if __name__ == '__main__':
        a = Alarm()
        a.Execute()
        while True:
            a.Execute()

except KeyboardInterrupt:
    print("(╯°□°）╯︵ ┻━┻")
    display.clear()
    GPIO.cleanup()
    killTransmitThread()





