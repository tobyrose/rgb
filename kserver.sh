echo "Killing flaschen server"
sudo kill $(ps aux | grep 'ft-server' | awk '{print $2}')
