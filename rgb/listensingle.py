import os
import sys
import subprocess
import time
from flask import abort,Flask, request
from pathlib import Path
import requests
from time import sleep
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageOps


options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 4
options.pixel_mapper_config = 'U-mapper'
options.parallel = 1
options.gpio_slowdown = 3
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
options.drop_privileges = False
options.pwm_lsb_nanoseconds=50
options.brightness = 75
matrix = RGBMatrix(options = options)

matrix.Clear()
#os.system("/home/pi/rgb/undocool.sh")
#time.sleep(0.5)
#os.system("/home/pi/rgb/docool.sh")

#exit()

sentinelfile = '/home/pi/rgb/imagechange'
sentinel = Path(sentinelfile)
currenturl = ''
imgpath = '/home/pi/rgb/listenimg/'
defimage = '/home/pi/rgb/law'

app = Flask(__name__)
@app.before_request
def limit_remote_addr():
    if not (request.remote_addr.startswith('192.168.91') or request.remote_addr.startswith('192.168.90')):
        abort(403)  # Forbidden
        
@app.route('/', methods=['GET'])
def gotimg():
    global currenturl
    print ('CURRENT URL AT START: '+currenturl)
    changed = False
    url = request.args.get('url')
    if url is not None:
        newurl = url

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
                exitc = 0
            else:
                # Get the shell to do it, it's way better than python
                exitc = os.system('wget -O '+imgpath+'newimg ' +currenturl)

                """
                imgdata = requests.get(currenturl)
                print(imgdata)
                print (imgdata.status_code)
                open(imgpath+'newimg', 'wb').write(imgdata.content)
                """

                """
                try:                
                    with Timeout(5): # timeout for image download
                        imgdata = requests.get(currenturl)
                        print(imgdata)
                        print (imgdata.status_code)
                    if imgdata.status_code == 200:
                        open(imgpath+'newimg', 'wb').write(imgdata.content)
                    else: 
                        raise Exception
                except:
                    print('no good')
                    os.system('cp '+defimage+' '+imgpath+'newimg')
                """


            if Path(imgpath+'newimg').is_file() and exitc == 0:
                print ('DOWNLOADED OK')
                os.system('mv '+imgpath+'newimg '+imgpath+'displayimg')

            else:
                print ('no file')
                os.system('cp '+defimage+' '+imgpath+'displayimg')
                # cp default image to '+imgpath+'displayimg'

            if (currenturl == 'def'):

                print ('Clearing rgb')
                matrix.Clear()

                # or 
                #print ('Showing demo')
                #os.system("/home/pi/rgb/undocool.sh")
                #matrix.Clear()
                #time.sleep(0.5)
                #os.system('/home/pi/rgb/docool.sh')

                

                #or 
                # image = Image.open(imgpath+'displayimg')
                # img = ImageOps.fit(image, (matrix.width, matrix.height), Image.ANTIALIAS)
                # matrix.SetImage(img.convert('RGB'))
                # print ("AND NOW DISPLAY THE IMAGE")


            else:
                #os.system("/home/pi/rgb/undocool.sh")
                image = Image.open(imgpath+'displayimg')
                #img = ImageOps.fit(image, (matrix.width, matrix.height), Image.ANTIALIAS)
                img = ImageOps.fit(image, (128, 128), Image.ANTIALIAS)
                matrix.Clear()
                matrix.SetImage(img.convert('RGB'))
                print ("AND NOW DISPLAY THE IMAGE")        


    else:
        print ('Didnt get var')
    return 'OK'

app.run(port=3000, host='192.168.90.196')

#https://i.scdn.co/image/ab67616d0000b27357df27ffa7a6215bf5c78cf6
