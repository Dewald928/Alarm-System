#!/usr/bin/python

# from gpiozero import Buzzer
from time import sleep
from pad4pi import rpi_gpio


# buzzer = Buzzer(26)


def print_key(key):
    # buzzer.on()
    # sleep(0.1)
    # buzzer.off()
    print(key)


try:
    factory = rpi_gpio.KeypadFactory()
    keypad = factory.create_4_by_3_keypad()  # makes assumptions about keypad layout and GPIO pin numbers

    keypad.registerKeyPressHandler(print_key)

    print("Press buttons on your keypad. Ctrl+C to exit.")
    while True:
        sleep(1)

except KeyboardInterrupt:
    print("Goodbye")
finally:
    keypad.cleanup()
