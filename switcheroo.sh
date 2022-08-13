#!/bin/bash

echo ""
echo "[ENTER] - Standard Switcheroo"
echo "[1]     - Start Flaschen Server"
echo "[2]     - Start Spotify Listener"
echo "[3]     - Kill All"
echo "[4]     - SSH"

read -t 5 -n 1 -p "Switcheroo? or wait 5 secs..."
if [ $? == 0 ] && [ "$REPLY" == "" ]; then
    echo ""
    echo 'Standard Switcheroo'
    if [ $(ps aux | grep 'ft-server' | grep -v grep | awk '{print $2}' | wc -c) -gt 1 ]; then
        echo "Killing flaschen server"
        echo "Starting Spotify listener"
        sudo kill $(ps aux | grep 'ft-server' | awk '{print $2}')
        cd /home/pi/rgb/
        nohup sudo python3 /home/pi/rgb/listensingle.py >/dev/null 2>&1 &
    elif [ $(ps aux | grep 'listensingle.py' | grep -v grep | awk '{print $2}' | wc -c) -gt 1 ]; then
        echo "Killing Spotify Listener"
        echo "Starting flaschen server"
        sudo kill $(ps aux | grep 'listensingle.py' | awk '{print $2}')
        cd /home/pi/
        nohup sudo /home/pi/sserver.sh >/dev/null 2>&1 &
    else
       echo "Couldn't find anything"
       echo "Firing up flaschen server"
       cd /home/pi/
       nohup sudo /home/pi/sserver.sh >/dev/null 2>&1 &
    fi
fi


if [ "$REPLY" == "1" ]; then
    echo ""
    echo 'Killing all and starting flaschen server'
    sudo kill $(ps aux | grep 'ft-server' | awk '{print $2}')
    sudo kill $(ps aux | grep 'listensingle.py' | awk '{print $2}')
    cd /home/pi/
    nohup sudo /home/pi/sserver.sh >/dev/null 2>&1 &
elif [ "$REPLY" == "2" ]; then
    echo ""
    echo 'Killing all and starting Spotify listener'
    sudo kill $(ps aux | grep 'ft-server' | awk '{print $2}')
    sudo kill $(ps aux | grep 'listensingle.py' | awk '{print $2}')
    cd /home/pi/rgb/
    nohup sudo python3 /home/pi/rgb/listensingle.py >/dev/null 2>&1 &
elif [ "$REPLY" == "3" ]; then
    echo ""
    echo 'Killing All'
    sudo kill $(ps aux | grep 'ft-server' | awk '{print $2}')
    sudo kill $(ps aux | grep 'listensingle.py' | awk '{print $2}')
elif [ "$REPLY" == "4" ]; then
    echo ""
    echo 'No Patience... '
    exit
fi

echo ""

exit



