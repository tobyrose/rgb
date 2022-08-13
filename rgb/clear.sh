sudo python3 /home/pi/rgb/clear.py; sleep 1; sudo kill $(ps aux | grep 'clear.py' | awk '{print $2}')
