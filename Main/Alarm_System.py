#!/usr/bin/env python

from time import clock
from Alarm_Class import Alarm


if __name__ == '__main__':
    r = Alarm()
    for i in range(10):
        startTime = clock()
        timeInterval = 1
        while (startTime + timeInterval > clock()):
            pass
        r.Execute()
    print('Exiting program...')