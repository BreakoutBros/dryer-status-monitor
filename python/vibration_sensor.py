import RPi.GPIO as GPIO
import time
import os
import httplib
import urllib


class PushoverSender:
    def __init__(self, user_key, api_key):
        self.user_key = user_key
        self.api_key = api_key

    def send_notification(self, text):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        post_data = {'user': self.user_key, 'token': self.api_key, 'message': text}
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode(post_data), {"Content-type": "application/x-www-form-urlencoded"})
        # print(conn.getresponse().read())


class DryerMonitor:
    poll_duration_secs = 30
    poll_hz = 60

    def __init__(self, gpio_bcm, pushover_sender):
        self.gpio = gpio_bcm
        self.pushover_sender = pushover_sender
        self.status = None

    def __enter__(self):
        self.push_startup_notification()
        self.init_gpio()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.push_close_notification()
        self.cleanup_gpio()

    def update_dryer_status(self):
        new_status = self._poll_gpio()
        # Send notification if status changed
        if new_status != self.status:
            if new_status:
                self.pushover_sender.send_notification('Dryer is On')
            else:
                self.pushover_sender.send_notification('Dryer is Off')
            self.status = new_status

    def init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.IN)

    def cleanup_gpio(self):
        GPIO.cleanup()

    def push_startup_notification(self):
        self.pushover_sender.send_notification('Dryer Monitor Started')

    def push_close_notification(self):
        self.pushover_sender.send_notification('Dryer Monitor Stopped')

    def _poll_gpio(self):
        start_time = time.time()
        end_time = start_time + DryerMonitor.poll_duration_secs
        count_high = 0
        count_low = 0
        while time.time() < end_time:
            if GPIO.input(self.gpio) != 0:
                count_high += 1
            else:
                count_low += 1
            time.sleep(1.0 / DryerMonitor.poll_hz)
        return count_high > 5


def get_key(filename):
    with open(filename) as f:
        key = f.read().strip()
    return key


def main():
    # Get Pushover keys from files
    user_key = get_key(os.path.join(os.path.dirname(__file__), 'user.key'))
    api_key = get_key(os.path.join(os.path.dirname(__file__), 'apitoken.key'))

    pushover_sender = PushoverSender(user_key, api_key)
    with DryerMonitor(21, pushover_sender) as dm:
        dm.update_dryer_status()
        while True:
            dm.update_dryer_status()

if __name__ == '__main__':
    main()
