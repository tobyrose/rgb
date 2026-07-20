#!/bin/bash

FLASCHEN_START="/home/pi/sserver.sh"
SPOTIFY_SCRIPT="/home/pi/rgb/listensingle.py"
CLOCK_SCRIPT="/home/pi/rgb/berlin_clock_switchable_seconds.py"

kill_flaschen() {
    sudo pkill -f "ft-server" 2>/dev/null || true
}

kill_spotify() {
    sudo pkill -f "$SPOTIFY_SCRIPT" 2>/dev/null || true
}

kill_clock() {
    sudo pkill -f "$CLOCK_SCRIPT" 2>/dev/null || true
}

kill_all() {
    echo "Stopping Flaschen server..."
    kill_flaschen

    echo "Stopping Spotify listener..."
    kill_spotify

    echo "Stopping Berlin Clock..."
    kill_clock
}

start_flaschen() {
    kill_all

    echo "Starting Flaschen server..."
    cd /home/pi/ || exit 1
    nohup sudo "$FLASCHEN_START" >/dev/null 2>&1 &
}

start_spotify() {
    kill_all

    echo "Starting Spotify listener..."
    cd /home/pi/rgb/ || exit 1
    nohup sudo python3 "$SPOTIFY_SCRIPT" >/dev/null 2>&1 &
}

start_clock() {
    kill_all

    echo "Starting Berlin Clock..."
    cd /home/pi/rgb/ || exit 1
    nohup sudo python3 "$CLOCK_SCRIPT" >/dev/null 2>&1 &
}

echo ""
echo "[1] - Start Flaschen Server"
echo "[2] - Start Spotify Listener"
echo "[3] - Start Berlin Clock"
echo "[4] - Kill All"
echo "[5] - SSH / Exit"
echo ""

REPLY=""
read -r -t 5 -n 1 -p "Switcheroo? Or wait 5 seconds... " REPLY
READ_STATUS=$?

echo ""
echo ""

if [ "$READ_STATUS" -ne 0 ]; then
    echo "No selection made."
    exit 0
fi

case "$REPLY" in
    1)
        start_flaschen
        ;;

    2)
        start_spotify
        ;;

    3)
        start_clock
        ;;

    4)
        echo "Killing all display processes..."
        kill_all
        ;;

    5)
        echo "Leaving display processes unchanged."
        ;;

    *)
        echo "Invalid selection: $REPLY"
        ;;
esac

echo ""
exit 0
