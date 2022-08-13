#!/usr/bin/env python
import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image

#if len(sys.argv) < 2:
#    sys.exit("Require an image argument")
#else:
#    image_file = sys.argv[1]

image = Image.open('/home/pi/rgb/law')
#image = Image.open('/home/pi/rgb/screen-QtCar-2020-06-08-14.33.45.png')

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 4
options.parallel = 1
options.gpio_slowdown = 2
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
options.pixel_mapper_config = 'U-mapper'
options.brightness = 50



matrix = RGBMatrix(options = options)

# Make image fit our screen.
image.thumbnail((128, 128), Image.ANTIALIAS)
#image.thumbnail((256, 128))
matrix.SetImage(image.convert('RGB'))

#time.sleep(10)

#matrix.Clear()

try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    matrix.Clear()
    sys.exit(0)
