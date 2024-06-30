import time

import network
import ntptime
from buzzer import Buzzer
from display import Display
from machine import Pin
from machine import RTC
from progressbar import ProgressBar

import config

b = Buzzer(Pin(21, Pin.OUT))
b.pulse(.1)

d = Display(Pin(18, Pin.OUT), Pin(17, Pin.OUT),
            [Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(5, Pin.OUT)])

d.begin(16, 2)
d.test_sentence()

p = ProgressBar(d, 16, 1)
p.begin()
p.display_progress(0.5)


# Configure and connect to the Wi-Fi network
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    d.clear()
    d.print("Connecting to WiFi")
    while not wlan.isconnected():
        time.sleep(1)

    print('WiFi connection established')
    d.clear()
    d.print("WiFi connected")
    print(wlan.ifconfig())


# Synchronize time with an NTP server
def sync_time():
    try:
        ntptime.host = 'pool.ntp.org'  # You can change this to another NTP server
        ntptime.settime()
        print('Time synchronized with NTP')
    except Exception as e:
        print('Error synchronizing with NTP:', e)


# Print the current time
def print_current_time():
    rtc = RTC()
    tm = rtc.datetime()
    print('Current Date and Time: ' + format_date(tm))


def format_date(tm: tuple) -> str:
    return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(tm[0], tm[1], tm[2], tm[4], tm[5], tm[6])


# Example usage
connect_wifi()
sync_time()
print_current_time()
