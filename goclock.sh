cd /home/pi/rpi-rgb-led-matrix/examples-api-use/
sudo /home/pi/rpi-rgb-led-matrix/examples-api-use/clock --led-cols=64 --led-rows=64 --led-slowdown-gpio=2 --led-gpio-mapping=adafruit-hat-pwm --led-chain=4 --led-pixel-mapper="U-mapper" --led-slowdown-gpio=2 --led-brightness=50 -f ../fonts/10x20.bdf -d "%A" -d "%H:%M:%S"
