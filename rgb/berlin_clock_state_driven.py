#!/usr/bin/env python3
"""
Berlin Clock for a 2x2 arrangement of four 64x64 HUB75 RGB LED panels.

Target:
    Raspberry Pi / Python 3.7+
    hzeller rpi-rgb-led-matrix Python bindings
    4 x 64x64 panels arranged as 128x128 using U-mapper

Rendering:
    Draws directly into the rgbmatrix framebuffer.
    No PIL image is created.
"""

import signal
import subprocess
import sys
import time
from datetime import datetime
from math import sqrt

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from rgbmatrix import graphics


# ============================================================
# MATRIX CONFIGURATION
# ============================================================

options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 4
options.parallel = 1
options.pixel_mapper_config = "U-mapper"

options.gpio_slowdown = 3
options.hardware_mapping = "adafruit-hat-pwm"
options.drop_privileges = False
options.pwm_lsb_nanoseconds = 50
options.brightness = 75

# Supported by normal hzeller builds. Comment out if your installed binding
# reports that this property does not exist.
options.pwm_bits = 8

matrix = RGBMatrix(options=options)


# ============================================================
# DISPLAY LAYOUT
# ============================================================

DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 128

# Set this to False to remove the flashing seconds lamp.
#
# True:
#   Shows the seconds lamp and uses four 22-pixel-high rows.
#
# False:
#   Hides the seconds lamp and enlarges the four rows vertically
#   to fill the display.
SHOW_SECONDS = False

# Optional NTP management.
#
# False is recommended initially. NTP normally uses negligible CPU and should
# not interfere with matrix refresh. Set True only if you want this clock app
# to enable NTP while running and restore the previous state on exit.
MANAGE_NTP = False

# Horizontal sizing remains the same in both modes.
#
# Four-lamp rows:
#   4 x 28 + 3 x 2 = 118 pixels, leaving 5 pixels each side.
WIDE_LAMP_WIDTH = 28
WIDE_LAMP_GAP = 2

# Eleven-lamp row:
#   11 x 9 + 10 x 2 = 119 pixels, leaving 4/5 pixels each side.
NARROW_LAMP_WIDTH = 9
NARROW_LAMP_GAP = 2

if SHOW_SECONDS:
    # 21-pixel seconds lamp at the top, followed by four equal rows.
    LAMP_HEIGHT = 22
    ROW_GAP = 3
    FIRST_ROW_Y = 27

    SECONDS_CENTRE_X = DISPLAY_WIDTH // 2
    SECONDS_CENTRE_Y = 12
    SECONDS_OUTER_RADIUS = 10
    SECONDS_INNER_RADIUS = 8
else:
    # Four 29-pixel-high rows with 3-pixel gaps:
    #   4 x 29 + 3 x 3 = 125 pixels
    # leaving 1 pixel at the top and 2 pixels at the bottom.
    LAMP_HEIGHT = 29
    ROW_GAP = 3
    FIRST_ROW_Y = 1

    # Defined for completeness, but not drawn in this mode.
    SECONDS_CENTRE_X = DISPLAY_WIDTH // 2
    SECONDS_CENTRE_Y = 0
    SECONDS_OUTER_RADIUS = 0
    SECONDS_INNER_RADIUS = 0

HOUR_5_Y = FIRST_ROW_Y
HOUR_1_Y = HOUR_5_Y + LAMP_HEIGHT + ROW_GAP
MINUTE_5_Y = HOUR_1_Y + LAMP_HEIGHT + ROW_GAP
MINUTE_1_Y = MINUTE_5_Y + LAMP_HEIGHT + ROW_GAP


def centred_positions(count, lamp_width, gap):
    """Return x coordinates that centre a row on the 128-pixel display."""
    total_width = count * lamp_width + (count - 1) * gap
    start_x = (DISPLAY_WIDTH - total_width) // 2
    return tuple(
        start_x + index * (lamp_width + gap)
        for index in range(count)
    )


WIDE_ROW_X = centred_positions(4, WIDE_LAMP_WIDTH, WIDE_LAMP_GAP)
NARROW_ROW_X = centred_positions(11, NARROW_LAMP_WIDTH, NARROW_LAMP_GAP)


# ============================================================
# COLOURS
# ============================================================

OFF_BORDER = graphics.Color(12, 12, 12)
OFF_INNER = graphics.Color(2, 2, 2)

RED_BORDER = graphics.Color(150, 10, 10)
RED_INNER = graphics.Color(255, 30, 30)

YELLOW_BORDER = graphics.Color(165, 120, 0)
YELLOW_INNER = graphics.Color(255, 220, 0)


# ============================================================
# PRECOMPUTED GEOMETRY
# ============================================================

def integer_sqrt(value):
    """
    Python 3.7-compatible integer square root.

    sqrt() is only used at startup while the seconds-lamp geometry is built.
    """
    return int(sqrt(value))


def make_circle_spans(radius):
    """
    Build horizontal spans for a filled circle.

    Each tuple is:
        (vertical offset, horizontal half-width)

    The geometry is calculated once at startup.
    """
    radius_squared = radius * radius
    spans = []

    for dy in range(-radius, radius + 1):
        half_width = integer_sqrt(radius_squared - dy * dy)
        spans.append((dy, half_width))

    return tuple(spans)


if SHOW_SECONDS:
    SECONDS_OUTER_SPANS = make_circle_spans(SECONDS_OUTER_RADIUS)
    SECONDS_INNER_SPANS = make_circle_spans(SECONDS_INNER_RADIUS)
else:
    SECONDS_OUTER_SPANS = ()
    SECONDS_INNER_SPANS = ()


# ============================================================
# OPTIONAL NTP MANAGEMENT
# ============================================================

previous_ntp_state = None


def command_output(command):
    """Run a command and return stripped stdout, or None on failure."""
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            check=False,
        )
    except OSError:
        return None

    if completed.returncode != 0:
        return None

    return completed.stdout.strip()


def get_ntp_state():
    """Return True/False for timedatectl's NTP setting, or None."""
    value = command_output(
        ["timedatectl", "show", "--property=NTP", "--value"]
    )

    if value is None:
        return None

    value = value.lower()

    if value in ("yes", "true", "1"):
        return True

    if value in ("no", "false", "0"):
        return False

    return None


def set_ntp_state(enabled):
    """Enable or disable systemd-managed network time."""
    try:
        completed = subprocess.run(
            [
                "timedatectl",
                "set-ntp",
                "true" if enabled else "false",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False

    return completed.returncode == 0


def enable_ntp_for_clock():
    """Remember the current NTP state, then enable NTP for this app."""
    global previous_ntp_state

    if not MANAGE_NTP:
        return

    previous_ntp_state = get_ntp_state()

    if previous_ntp_state is True:
        print("NTP is already enabled.")
        return

    if set_ntp_state(True):
        print("NTP enabled while Berlin Clock is running.")
    else:
        print("Warning: unable to enable NTP with timedatectl.")


def restore_ntp_state():
    """Restore the NTP setting that existed before the clock started."""
    if not MANAGE_NTP:
        return

    if previous_ntp_state is None:
        print("NTP state was unknown; leaving it unchanged.")
        return

    if set_ntp_state(previous_ntp_state):
        state_name = "enabled" if previous_ntp_state else "disabled"
        print("NTP restored to {0}.".format(state_name))
    else:
        print("Warning: unable to restore the previous NTP state.")


# ============================================================
# SHUTDOWN HANDLING
# ============================================================

running = True


def request_shutdown(signum=None, frame=None):
    """
    Ask the main loop to stop.

    Explicit signal handling makes Ctrl+C and service shutdown more reliable,
    especially when the rgbmatrix library is driving the display continuously.
    """
    global running
    running = False


signal.signal(signal.SIGINT, request_shutdown)
signal.signal(signal.SIGTERM, request_shutdown)


# ============================================================
# DRAWING HELPERS
# ============================================================

def fill_rectangle(canvas, x, y, width, height, colour):
    """Fill a rectangle directly in the rgbmatrix framebuffer."""
    right = x + width - 1

    for current_y in range(y, y + height):
        graphics.DrawLine(
            canvas,
            x,
            current_y,
            right,
            current_y,
            colour,
        )


def draw_lamp(canvas, x, y, width, height, lit, colour_name):
    """Draw one rectangular Berlin Clock lamp."""
    if lit:
        if colour_name == "red":
            border_colour = RED_BORDER
            inner_colour = RED_INNER
        else:
            border_colour = YELLOW_BORDER
            inner_colour = YELLOW_INNER
    else:
        border_colour = OFF_BORDER
        inner_colour = OFF_INNER

    # One-pixel border.
    fill_rectangle(
        canvas,
        x,
        y,
        width,
        height,
        border_colour,
    )

    # Inner illuminated face.
    fill_rectangle(
        canvas,
        x + 1,
        y + 1,
        width - 2,
        height - 2,
        inner_colour,
    )


def draw_row(
    canvas,
    x_positions,
    y,
    lamp_width,
    lit_count,
    default_colour,
    red_indices=(),
):
    """Draw one complete Berlin Clock row."""
    for index, x in enumerate(x_positions):
        colour_name = (
            "red"
            if index in red_indices
            else default_colour
        )

        draw_lamp(
            canvas=canvas,
            x=x,
            y=y,
            width=lamp_width,
            height=LAMP_HEIGHT,
            lit=index < lit_count,
            colour_name=colour_name,
        )


def draw_circle_spans(canvas, centre_x, centre_y, spans, colour):
    """Draw a precomputed filled circle using horizontal framebuffer lines."""
    for dy, half_width in spans:
        graphics.DrawLine(
            canvas,
            centre_x - half_width,
            centre_y + dy,
            centre_x + half_width,
            centre_y + dy,
            colour,
        )


def draw_seconds_lamp(canvas, lit):
    """Draw the top blinking seconds lamp."""
    if lit:
        outer_colour = YELLOW_BORDER
        inner_colour = YELLOW_INNER
    else:
        outer_colour = OFF_BORDER
        inner_colour = OFF_INNER

    draw_circle_spans(
        canvas,
        SECONDS_CENTRE_X,
        SECONDS_CENTRE_Y,
        SECONDS_OUTER_SPANS,
        outer_colour,
    )

    draw_circle_spans(
        canvas,
        SECONDS_CENTRE_X,
        SECONDS_CENTRE_Y,
        SECONDS_INNER_SPANS,
        inner_colour,
    )


# ============================================================
# CLOCK RENDERING
# ============================================================

def draw_clock(canvas, now):
    """Render one complete Berlin Clock frame."""
    canvas.Clear()

    hour = now.hour
    minute = now.minute
    second = now.second

    # Real Berlin Clock convention: top lamp alternates each second.
    # It can be disabled with SHOW_SECONDS at the top of the file.
    if SHOW_SECONDS:
        draw_seconds_lamp(canvas, lit=(second % 2 == 0))

    # Four lamps, each representing five hours.
    draw_row(
        canvas=canvas,
        x_positions=WIDE_ROW_X,
        y=HOUR_5_Y,
        lamp_width=WIDE_LAMP_WIDTH,
        lit_count=hour // 5,
        default_colour="red",
    )

    # Four lamps, each representing one hour.
    draw_row(
        canvas=canvas,
        x_positions=WIDE_ROW_X,
        y=HOUR_1_Y,
        lamp_width=WIDE_LAMP_WIDTH,
        lit_count=hour % 5,
        default_colour="red",
    )

    # Eleven lamps, each representing five minutes.
    # Lamps 3, 6 and 9 are red for quarter hours.
    draw_row(
        canvas=canvas,
        x_positions=NARROW_ROW_X,
        y=MINUTE_5_Y,
        lamp_width=NARROW_LAMP_WIDTH,
        lit_count=minute // 5,
        default_colour="yellow",
        red_indices=(2, 5, 8),
    )

    # Four lamps, each representing one minute.
    draw_row(
        canvas=canvas,
        x_positions=WIDE_ROW_X,
        y=MINUTE_1_Y,
        lamp_width=WIDE_LAMP_WIDTH,
        lit_count=minute % 5,
        default_colour="yellow",
    )


# ============================================================
# STATE AND TIMING
# ============================================================

def clock_state(now):
    """
    Return only values that can change the displayed image.

    With seconds disabled, seconds are excluded, so the matrix is updated only
    when the displayed minute changes.
    """
    state = (
        now.hour // 5,
        now.hour % 5,
        now.minute // 5,
        now.minute % 5,
    )

    if SHOW_SECONDS:
        state += (now.second % 2,)

    return state


def sleep_until_possible_change():
    """
    Sleep until the next relevant display boundary.

    Seconds mode wakes at the next whole second.
    No-seconds mode wakes at the next whole minute.
    """
    current_time = time.time()

    if SHOW_SECONDS:
        target = int(current_time) + 1
    else:
        target = (int(current_time) // 60 + 1) * 60

    while running:
        remaining = target - time.time()

        if remaining <= 0:
            return

        time.sleep(min(0.25, remaining))


# ============================================================
# MAIN
# ============================================================

def main():
    canvas = matrix.CreateFrameCanvas()
    previous_state = None

    mode = "with seconds lamp" if SHOW_SECONDS else "without seconds lamp"
    print("Berlin Clock running on 128x128 RGB matrix ({0}).".format(mode))

    if SHOW_SECONDS:
        print("Display updates only when the visible second state changes.")
    else:
        print("Display updates only when the displayed minute changes.")

    print("Stop with: sudo pkill -f berlin_clock_state_driven.py")

    enable_ntp_for_clock()

    try:
        while running:
            now = datetime.now()
            state = clock_state(now)

            # Do not clear, redraw or swap unless the visible state changed.
            if state != previous_state:
                draw_clock(canvas, now)
                canvas = matrix.SwapOnVSync(canvas)
                previous_state = state

            sleep_until_possible_change()

    finally:
        restore_ntp_state()

        try:
            canvas.Clear()
            canvas = matrix.SwapOnVSync(canvas)
        except Exception:
            pass

        try:
            matrix.Clear()
        except Exception:
            pass

        print("\nStopped.")


if __name__ == "__main__":
    main()
