#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
import RPi.GPIO as GPIO

# Define pins for RPi
RST = 27
DC = 25
BL = 18

# SPI configuration
bus = 0
device = 0

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(BL, GPIO.OUT)

# Initialize SPI
spi = SPI.SpiDev(bus, device)
spi.max_speed_hz = 90000000

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# ILI9341 commands
ILI9341_SWRESET = 0x01
ILI9341_SLPOUT = 0x11
ILI9341_DISPON = 0x29
ILI9341_CASET = 0x2A
ILI9341_PASET = 0x2B
ILI9341_RAMWR = 0x2C
ILI9341_MADCTL = 0x36
ILI9341_COLMOD = 0x3A

# Helper functions to send commands and data
def send_command(cmd):
    GPIO.output(DC, GPIO.LOW)
    spi.writebytes([cmd])

def send_data(data):
    GPIO.output(DC, GPIO.HIGH)
    if isinstance(data, list):
        spi.writebytes(data)
    else:
        spi.writebytes([data])

# Initialize display
def init_display():
    GPIO.output(RST, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(RST, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RST, GPIO.HIGH)
    time.sleep(0.1)
    
    send_command(ILI9341_SWRESET)
    time.sleep(0.1)
    
    send_command(ILI9341_SLPOUT)
    time.sleep(0.1)
    
    send_command(ILI9341_DISPON)
    time.sleep(0.1)
    
    send_command(ILI9341_MADCTL)
    send_data(0x48)
    
    send_command(ILI9341_COLMOD)
    send_data(0x55)

# Function to fill the screen with a color
def fill_screen(color):
    send_command(ILI9341_CASET)
    send_data([0x00, 0x00, 0x00, 0xEF])
    
    send_command(ILI9341_PASET)
    send_data([0x00, 0x00, 0x01, 0x3F])
    
    send_command(ILI9341_RAMWR)
    
    high_byte = (color >> 8) & 0xFF
    low_byte = color & 0xFF
    data = [high_byte, low_byte] * (240 * 320)
    
    send_data_in_chunks(data)

def send_data_in_chunks(data, chunk_size=4096):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        send_data(chunk)

# Function to measure FPS
def measure_fps(duration=5):
    colors = [0x0000, 0xF800, 0x07E0, 0x001F, 0xFFFF]
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < duration:
        for color in colors:
            fill_screen(color)
            frame_count += 1
    
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time
    logging.info(f"FPS: {fps:.2f}")

# Main code
try:
    init_display()
    GPIO.output(BL, GPIO.HIGH)
    
    measure_fps()
    
    logging.info("Done!")
except KeyboardInterrupt:
    logging.info("Exiting program")
finally:
    GPIO.cleanup()
