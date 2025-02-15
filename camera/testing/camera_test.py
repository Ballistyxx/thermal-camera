#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2, Preview

# Import the LCD library
sys.path.append("..")
from lib import LCD_2inch4

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0

logging.basicConfig(level=logging.DEBUG)

try:
    # Initialize the display
    disp = LCD_2inch4.LCD_2inch4()
    disp.Init()
    disp.clear()
    disp.bl_DutyCycle(50)

    # Initialize Picamera2
    picam2 = Picamera2()

    # Configure the camera
    config = picam2.create_preview_configuration(main={"size": (disp.width, disp.height)})
    picam2.configure(config)
    picam2.start()

    # Main loop to display the camera feed
    while True:
        # Capture an image as an array
        image_array = picam2.capture_array()

        # Convert to PIL image for processing
        image = Image.fromarray(image_array)
        image = image.resize((disp.width, disp.height))

        # Display the image on the LCD
        disp.ShowImage(image)
        time.sleep(0.05)

except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("Exiting program")
finally:
    picam2.close()
    disp.module_exit()
    logging.info("Program terminated")
