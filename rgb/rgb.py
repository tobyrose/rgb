import os
import sys
import time
from pathlib import Path
import requests
from time import sleep
import signal
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageOps

class Timeout():
    """ Timeout for use with the `with` statement. """

    class TimeoutException(Exception):
        """ Simple Exception to be called on timeouts. """
        pass

    def _timeout(signum, frame):
        """ Raise an TimeoutException.

        This is intended for use as a signal handler.
        The signum and frame arguments passed to this are ignored.

        """
        raise Timeout.TimeoutException()

    def __init__(self, timeout=10):
        self.timeout = timeout
        signal.signal(signal.SIGALRM, Timeout._timeout)

    def __enter__(self):
        signal.alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        signal.alarm(0)
        return exc_type is Timeout.TimeoutException

sentinelfile = '/home/pi/rgb/imagechange'
sentinel = Path(sentinelfile)
currenturl = ''
imgpath = '/home/pi/rgb/listenimg/'
defimage = '/home/pi/rgb/law'


options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 4
options.pixel_mapper_config = 'U-mapper'
options.parallel = 1
options.gpio_slowdown = 3
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
matrix = RGBMatrix(options = options)

f = open(sentinel, "w+")
f.write('def')
f.close()

while True:
    changed = False
    if sentinel.is_file():
        f = open(sentinelfile, "r") # URL is in this file
        newurl = f.read()
        f.close()
        os.remove(sentinelfile) # Remove it

        if currenturl != newurl:
            print ('Changed')
            print (newurl)
            currenturl = newurl
            changed = True
        else:
            print ('Samesame')

        if changed == True:
            if currenturl == 'def':
                os.system('cp '+defimage+' '+imgpath+'newimg')
                print ('Copied to new')
            else:
                try:                
                    with Timeout(5): # timeout for image download
                        imgdata = requests.get(currenturl)
                        print(imgdata)
                    if imgdata.status_code == 200:
                        open(imgpath+'newimg', 'wb').write(imgdata.content)
                    else: 
                        raise Exception
                except:
                    print('no good')
                    os.system('cp '+defimage+' '+imgpath+'newimg')

            if Path(imgpath+'newimg').is_file():
                os.system('mv '+imgpath+'newimg '+imgpath+'displayimg')

            else:
                print ('no file')
                # cp default image to '+imgpath+'displayimg'
            image = Image.open(imgpath+'displayimg')
            #image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
            img = ImageOps.fit(image, (matrix.width, matrix.height), Image.ANTIALIAS)
            matrix.SetImage(img.convert('RGB'))
            print ("AND NOW DISPLAY THE IMAGE")

    time.sleep(1)


