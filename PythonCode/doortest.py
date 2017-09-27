#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import threading

switches = [16, 12]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(switches, GPIO.IN, pull_up_down=GPIO.PUD_UP)
write_lock = threading.Lock()


def handle(pin):
    state = GPIO.input(pin)
    write_lock.acquire()
    print(str(pin)+str(state), flush=True)
    write_lock.release()

for pin in switches: GPIO.add_event_detect(pin, GPIO.BOTH, handle)

while True: time.sleep(1e6)



