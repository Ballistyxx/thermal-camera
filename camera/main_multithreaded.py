#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import threading
import logging
import math
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from picamera2 import Picamera2
import board
import adafruit_mlx90640
import RPi.GPIO as GPIO
import psutil

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

# ILI9341 setup and MLX90640 setup
MINTEMP = 25.0
MAXTEMP = 45.0
COLORDEPTH = 1000
pause_frame = False


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

# Initialize MLX90640
mlx = adafruit_mlx90640.MLX90640(board.I2C())
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ

# Heatmap and image processing
heatmap = (
    (0.0, (0.5, 0.5, 0.5)), #color of relatively useless 'ambient temp' pixels 
    (0.25, (0, 0, 0.5)),
    (0.40, (0, 0.5, 0)),
    (0.60, (0.5, 0, 0)),
    (0.80, (0.75, 0.75, 0)),
    (0.90, (1.0, 0.75, 0)),
    (1.00, (1.0, 1.0, 1.0)),
)

colormap = [0] * COLORDEPTH

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-((x - b) ** 2) / (2 * c**2)) + d

def gradient(x, width, cmap, spread=1):
    width = float(width)
    r = sum(
        gaussian(x, p[1][0], p[0] * width, width / (spread * len(cmap))) for p in cmap
    )
    g = sum(
        gaussian(x, p[1][1], p[0] * width, width / (spread * len(cmap))) for p in cmap
    )
    b = sum(
        gaussian(x, p[1][2], p[0] * width, width / (spread * len(cmap))) for p in cmap
    )
    r = int(constrain(r * 255, 0, 255))
    g = int(constrain(g * 255, 0, 255))
    b = int(constrain(b * 255, 0, 255))
    return r, g, b

for i in range(COLORDEPTH):
    colormap[i] = gradient(i, COLORDEPTH, heatmap)

def capture_frame():
    frame = [0] * 768
    while True:
        try:
            mlx.getFrame(frame)
            break
        except ValueError:
            continue
    return frame

def get_cpu_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return float(temp.replace("temp=", "").replace("'C\n", ""))

def get_cpu_load():
    return psutil.cpu_percent(interval=1)

def generate_heatmap_overlay(frame, zoom_factor=1.0, x_shift=0, y_shift=0):
    pixels = [0] * 768
    min_temp = float('inf')
    max_temp = float('-inf')
    min_idx = max_idx = 0

    for i, pixel in enumerate(frame):
        if pixel < min_temp:
            min_temp = pixel
            min_idx = i
        if pixel > max_temp:
            max_temp = pixel
            max_idx = i

        coloridx = map_value(pixel, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1)
        coloridx = int(constrain(coloridx, 0, COLORDEPTH - 1))
        pixels[i] = colormap[coloridx]

    img = Image.new("RGB", (32, 24))
    img.putdata(pixels)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Apply zoom only to the thermal image data
    new_width = int(32 * zoom_factor)
    new_height = int(24 * zoom_factor)
    img = img.resize((new_width, new_height), Image.BICUBIC)

    # Apply shifts to the heatmap
    img = img.crop((
        x_shift,
        y_shift,
        x_shift + 32,
        y_shift + 24
    ))

    # Resize heatmap image to match the display size
    img = img.resize((disp.width, disp.height), Image.BICUBIC)

    # Draw crosses and temperature values
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    #min_x, min_y = (min_idx % 32) * (disp.width // 32), (min_idx // 32) * (disp.height // 24)
    max_x, max_y = (max_idx % 32 - 3) * (disp.width // 32)*2, (24 -(max_idx // 24) + 4) * (disp.height // 24) + y_shift

    # Draw cross at hottest point (red cross)
    draw.line((max_x - 5, max_y, max_x + 5, max_y), fill="red", width=2)
    draw.line((max_x, max_y - 5, max_x, max_y + 5), fill="red", width=2)

    text_image = Image.new("RGBA", draw.textsize(f"\n      {max_temp:.1f}C", font=font))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), f"\n      {max_temp:.1f}C", fill="red", font=font)
    text_image = text_image.rotate(180)

    # Paste the rotated text back onto the main image
    img.paste(text_image, (max_x - text_image.width // 2, max_y - text_image.height // 2), text_image)

    return img

    
    
    

# GPIO setup for buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button 3
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button 2
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button 1

def save_screenshot(blended_image):
   
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    # Find the next available filename
    i = 1
    while True:
        filename = os.path.join(screenshot_dir, f"{i:04d}.png")
        if not os.path.exists(filename):
            break
        i += 1
    
    # Save the screenshot
    
    
    blended_image.save(filename)  
    return filename

def show_message_on_screen(message, duration=1):
    global blended_image
    # Create a blank image
    overlay = Image.new("RGBA", (disp.width, disp.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    # Calculate text size and position
    text_size = draw.textsize(message, font=font)
    text_x = (disp.width - text_size[0]) // 2
    text_y = (disp.height - text_size[1]) // 2

    # Draw the message on the overlay
    draw.text((text_x, text_y), message, fill="white", font=font)

    # Blend the message with the current display image
    blended_message = Image.alpha_composite(blended_image.convert("RGBA"), overlay)
    disp.ShowImage(blended_message.convert("RGB"))

    # Wait for the specified duration
    time.sleep(duration)

def button1_pressed(channel):
    os.system("sudo shutdown -h now")
    
def button2_pressed(channel):
    global pause_frame
    pause_frame = not pause_frame
    
    
def button3_pressed(channel):
    global blended_image
    with image_lock:
        filename = save_screenshot(blended_image)
    show_message_on_screen(f"Screenshot saved as {filename}")

GPIO.add_event_detect(16, GPIO.FALLING, callback=button1_pressed, bouncetime=1000)
GPIO.add_event_detect(20, GPIO.FALLING, callback=button2_pressed, bouncetime=1000)
GPIO.add_event_detect(21, GPIO.FALLING, callback=button3_pressed, bouncetime=1000)

# Thread-safe lock for shared resources
thermal_image = None
camera_image = None
image_lock = threading.Lock()
zoom_factor=2
x_shift=9
y_shift=13


def update_camera():
    global camera_image
    while True:
        # Capture camera image
        image_array = picam2.capture_array()
        with image_lock:
            camera_image = Image.fromarray(image_array)

            # Rotate the camera image 90 degrees clockwise
            camera_image = camera_image.rotate(270, expand=True)

            # Resize camera image to match the display size (after rotation)
            camera_image = camera_image.resize((disp.width, disp.height))

        time.sleep(0.033)  # ~30 FPS for the camera

def update_thermal():
    global thermal_image
    while True:
        # Capture heat map
        frame = capture_frame()
        with image_lock:
            thermal_image = generate_heatmap_overlay(frame, zoom_factor, x_shift, y_shift)

            # Resize the thermal image to match the display size
            thermal_image = thermal_image.resize((disp.width, disp.height))

        time.sleep(0.25)  # Thermal sensor refreshes at ~4 FPS

def display_image():
    global camera_image, thermal_image, pause_frame, blended_image
    while True:
        if not pause_frame:
            with image_lock:
                if camera_image is not None and thermal_image is not None:
                    # Ensure both images are the same size
                    camera_rgba = camera_image.convert("RGBA")
                    thermal_rgba = thermal_image.convert("RGBA")

                    # Blend the images
                    blended_image = Image.blend(camera_rgba, thermal_rgba, 0.75)

                    # Display the blended image on the LCD
                    disp.ShowImage(blended_image.convert("RGB"))  # Convert back to RGB for display
                elif camera_image is not None:
                    # If thermal image is not available, display only the camera image
                    disp.ShowImage(camera_image.convert("RGB"))

        time.sleep(0.033)  # ~30 FPS display refresh rate



# Start threads
camera_thread = threading.Thread(target=update_camera, daemon=True)
thermal_thread = threading.Thread(target=update_thermal, daemon=True)
display_thread = threading.Thread(target=display_image, daemon=True)

camera_thread.start()
thermal_thread.start()
display_thread.start()

try:
    while True:
        time.sleep(1)  # Keep the main thread alive
except KeyboardInterrupt:
    logging.info("Exiting program")
finally:
    picam2.close()
    disp.module_exit()
    GPIO.cleanup()
    logging.info("Program terminated")
