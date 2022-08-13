import time
import sys
from io import BytesIO
from PIL import Image
import sys,os
import requests

url="https://i.scdn.co/image/ab67616d0000b27357df27ffa7a6215bf5c78cf6"
os.system('wget {}'.format(url))


#imageURL="https://i.scdn.co/image/ab67616d0000485157df27ffa7a6215bf5c78cf6"
#response = requests.get(imageURL)
#image = Image.open(BytesIO(response.content))
#image.thumbnail((64, 64), Image.ANTIALIAS)

#image.save('testmovie1.png')


#sudo fim -d /dev/fb0 -T 1 --autoheight -q test.jpeg
#sudo fbi -d /dev/fb0 -T 1 -noverbose -autozoom test.jpeg


"""
url0="https://i.scdn.co/image/ab67616d0000485157df27ffa7a6215bf5c78cf6"
url2="https://i.scdn.co/image/ab67616d0000b27357df27ffa7a6215bf5c78cf6"
os.system('wget -O thisimg {}'.format(url2))
os.system('sudo fbi -d /dev/fb0 -T 1 -noverbose -autozoom thisimg')
time.sleep(5)
os.system('wget -O thisimg {}'.format(url0))
os.system('sudo fbi -d /dev/fb0 -T 1 -noverbose -autozoom thisimg')
"""
