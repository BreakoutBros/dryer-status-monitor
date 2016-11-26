import RPi.GPIO as GPIO
import signal
import sys
import time
import os
from datetime import datetime
import httplib, urllib

# Declared at module scope so cleanup function can use it
pushover_sender = None


class PushoverSender:
    def __init__(self, user_key, api_key):
        self.user_key = user_key
        self.api_key = api_key

    def send_notification(self, text):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        post_data = {'user': self.user_key, 'token': self.api_key, 'message': text}
        conn.request("POST", "/1/messages.json",
          urllib.urlencode(post_data), {"Content-type": "application/x-www-form-urlencoded"})
        print(conn.getresponse().read())


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
    if pushover_sender is not None:
        pushover_sender.send_notification('Dryer monitor stopped')


def get_key(filename):
    with open(filename) as f:
        key = f.read().strip()
    return key



def main_loop():
    # Setup GPIO
    vib_pin = 21
    init_gpio_input(vib_pin)

    # Construct file names using relative path
    status_file = os.path.join(os.path.dirname(__file__), 'dryer_status.txt')
    user_key_file = os.path.join(os.path.dirname(__file__), 'user.key')
    api_key_file = os.path.join(os.path.dirname(__file__), 'apitoken.key')

    # Get Pushover keys from files
    user_key = get_key(user_key_file)
    api_key = get_key(api_key_file)

    pushover_sender = PushoverSender(user_key, api_key)
    pushover_sender.send_notification('Dryer Monitor Started')

    last_status = None
    while True:
        low, high = poll_gpio(10, 100, vib_pin)
        status = 'Dryer Status: '
        if high > 1:
            new_status = True
            status += 'On\n'
        else:
            new_status = False
            status += 'Off\n'

        if last_status != new_status
            if new_status:
                pushover_sender.send_notification('Dryer is running')
            else:
                pushover_sender.send_notification('Dryer is off')
            last_status = new_status

        with open(status_file, 'w') as f:
            status += 'Updated: ' + str(datetime.now())
            f.write(status)


def main():
    try:
        # Catch signals to do GPIO cleanup and push notification before exiting
        signal.signal(signal.SIGINT, signal_handler)
        main_loop()
    finally:
        cleanup()


if __name__ == '__main__':
    main()
