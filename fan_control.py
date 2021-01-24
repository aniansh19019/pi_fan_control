#!/usr/bin/python3

# This script should run in the background on raspberry pi boot
# The second script should be used to view fan stats and to control the fan

import RPi.GPIO as GPIO
import subprocess
import time
# from multiprocessing import shared_memory as shm

FAN_PIN = 12  # pwm pin to which the fan control is connected, CHECK PIN NUMBERINGS CAREFULLY!
PWM_FREQ = 10  # pwm frequency, change this if the fan makes noise or if the fan misbehaves

ON_THRESHOLD = 65  # temperature above which the fan starts
OFF_THRESHOLD = 55  # temperature below which the fan stops
THROTTLE_THRESHOLD = 75  # temperature above which the fan should spin at maximum speed

# the lower limit on the duty cycle on the fan's pwm pin (The fan does not spin below this)
MIN_PWM = 20


SLEEP_INTERVAL = 5  # how often to check for a temperature change (in second)

GPIO.setwarnings(False)  # do not display warnings
GPIO.setmode(GPIO.BOARD)  # set pin numbering mode
GPIO.setup(FAN_PIN, GPIO.OUT)  # set fan pin to output

fan = GPIO.PWM(FAN_PIN, PWM_FREQ)  # fan pwm object
fan_on = False  # a control variable to see if the fan is on or off
fan_speed = 0  # variable to store the fan speed as % duty cycle

# fan_ctl_speed_Value = shm



# This function taken from https://howchoo.com/g/ote2mjkzzta/control-raspberry-pi-fan-temperature-python

def get_temp():
    """Get the core temperature.
    Run a shell script to get the core temp and parse the output.
    Raises:
        RuntimeError: if response cannot be parsed.
    Returns:
        float: The core temperature in degrees Celsius.
    """
    output = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True)
    temp_str = output.stdout.decode()
    try:
        return float(temp_str.split('=')[1].split('\'')[0])
    except (IndexError, ValueError):
        raise RuntimeError('Could not parse temperature output.')


if __name__ == '__main__':
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

    while True:
        temp = get_temp()

        if temp > THROTTLE_THRESHOLD:  # if the temperature goes above the throttle limit, run fan at full speed
            if not fan_on:
                fan_speed = 100
                fan.start(fan_speed)
                fan_on = True
            elif fan_speed != 100:
                fan_speed = 100
                fan.ChangeDutyCycle(fan_speed)

        elif temp > ON_THRESHOLD:  # if the temperature goes above the ON Threshold, run the fans at a speed proportional to the temperature
            fan_speed = (temp - OFF_THRESHOLD) / \
                (THROTTLE_THRESHOLD - OFF_THRESHOLD)
            fan_speed *= (100 - MIN_PWM)
            fan_speed += MIN_PWM
            fan_speed = round(fan_speed)
            # fan_ctl_speed_shm.buf[0] = fan_speed # write fan_speed to shared memory
            print(fan_speed)
            if not fan_on:
                fan.start(fan_speed)
                fan_on = True
            else:
                fan.ChangeDutyCycle(fan_speed)

        elif temp < OFF_THRESHOLD:  # if the temperature dips below the OFF Threshold, turn off the fan completely
            if fan_on:
                fan.stop()
                fan_speed = 0
                fan_on = False

        # sleep before sampling the temperature again
        time.sleep(SLEEP_INTERVAL)
