#!/usr/bin/env python

import time
from Alarm_Class import Alarm
import RPi.GPIO as GPIO

try:

    if __name__ == '__main__':
        a = Alarm()
        a.Execute()
        while True:
            a.Execute()

except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()

