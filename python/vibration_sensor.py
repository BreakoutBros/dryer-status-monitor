import RPi.GPIO as GPIO
import signal
import sys
import time
from datetime import datetime


def signal_handler(signal, frame):
    cleanup()
    sys.exit(0)


def init_gpio_input(bcm_pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm_pin, GPIO.IN)


def poll_gpio(duration_secs, frequency_hz, input_pin):
    start_time = time.time()
    end_time = start_time + duration_secs
    count_high = 0
    count_low = 0
    while time.time() < end_time:
        if GPIO.input(input_pin) == 0:
            count_low += 1
        else:
            count_high += 1
        time.sleep(1.0 / frequency_hz)
    return count_low, count_high


def cleanup():
    GPIO.cleanup()


def main_loop():
    vib_pin = 21
    init_gpio_input(vib_pin)
    while True:
        low, high = poll_gpio(10, 100, vib_pin)
        status = 'Dryer Status: '
        if high > 1:
            status += 'On\n'
        else:
            status += 'Off\n'
        with open('dryer_status.txt', 'w') as f:
            status += 'Updated: ' + str(datetime.now())
            f.write(status)


def main():
    try:
        signal.signal(signal.SIGINT, signal_handler)
        main_loop()
    finally:
        cleanup()


if __name__ == '__main__':
    main()
