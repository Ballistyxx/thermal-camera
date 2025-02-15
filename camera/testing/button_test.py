import RPi.GPIO as GPIO
import time
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button1_pressed(channel):
    #os.system("sudo shutdown -h now")
    print("1")
    
def button2_pressed(channel): 
    print("2")
    
def button3_pressed(channel):
    print("3")

GPIO.add_event_detect(16, GPIO.FALLING, callback=button1_pressed, bouncetime=1000)
GPIO.add_event_detect(20, GPIO.FALLING, callback=button2_pressed, bouncetime=1000)
GPIO.add_event_detect(21, GPIO.FALLING, callback=button3_pressed, bouncetime=1000)
while 1:
    time.sleep(1)
