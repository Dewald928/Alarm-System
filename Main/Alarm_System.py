#!/usr/bin/env python

import time
from Alarm_Class import Alarm


if __name__ == '__main__':
    a = Alarm()
    a.Execute()
    while True:
        a.Execute()

    print('Exiting program...')