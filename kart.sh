echo "Killing Spotify Art"
sudo kill $(ps aux | grep 'listensingle.py' | awk '{print $2}')
