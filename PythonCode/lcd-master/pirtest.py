import RPi.GPIO as GPIO
import time
import lcddriver

display = lcddriver.lcd()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)         #Read output from PIR motion sensor
GPIO.setup(17, GPIO.OUT)         #LED output pin
while True:
	print("No intruders")
	i=GPIO.input(4)
	if i==0:                 #When output from motion sensor is LOW
		print("No intruders")
		display.lcd_clear() 
		GPIO.output(17, 0)  #Turn OFF LED
		time.sleep(0.1)
	elif i==1:               #When output from motion sensor is HIGH
		print ("Intruder detected")
		display.lcd_display_string("Intruder detected!", 1)
		GPIO.output(17, 1)  #Turn ON LED
		time.sleep(0.1)
