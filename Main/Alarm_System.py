#!/usr/bin/env python

from random import randint
from time import clock
from Alarm_Class import RobotMaid


if __name__ == '__main__':
    r = RobotMaid()
    for i in range(10):
        startTime = clock()
        timeInterval = 1
        while (startTime + timeInterval > clock()):
            pass
        r.Execute()
    print('Exiting program...')