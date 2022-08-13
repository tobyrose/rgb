from rgbmatrix import RGBMatrix, RGBMatrixOptions
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.gpio_slowdown = 3
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
options.drop_privileges = False
matrix = RGBMatrix(options = options)

matrix.Clear()
exit()
