import os
from flask import abort,Flask, request
import time
import subprocess

"""
This just listens for a url of an image & writes a sentinel picked up by a 2nd script
"""
sentinel = '/home/pi/rgb/imagechange'

app = Flask(__name__)
@app.before_request
def limit_remote_addr():
    if not (request.remote_addr.startswith('192.168.91') or request.remote_addr.startswith('192.168.90')):
        abort(403)  # Forbidden
        
@app.route('/', methods=['GET'])
def gotimg():
    url = request.args.get('url')
    if url is not None:
        f = open(sentinel, "w+")
        f.write(url)
        f.close()
    else:
        print ('Didnt get var')
    return 'OK'

app.run(port=3000, host='192.168.90.196')

#https://i.scdn.co/image/ab67616d0000b27357df27ffa7a6215bf5c78cf6