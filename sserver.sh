echo "Starting flaschen server"
cd /home/pi/flaschen-taschen/server
sudo ./ft-server --led-cols=64 --led-rows=64 --led-slowdown-gpio=2 --led-gpio-mapping=adafruit-hat-pwm --led-chain=4 --led-pixel-mapper="U-mapper" --led-slowdown-gpio=2 --led-brightness=50

