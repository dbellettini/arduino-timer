from buzzer import Buzzer
from display import Display
from machine import RTC
from progressbar import ProgressBar


class PomoTimer:
    def __init__(self, display: Display, progress_bar: ProgressBar, buzzer: Buzzer, rtc: RTC):
        self.display = display
        self.progress_bar = progress_bar
        self.buzzer = buzzer
        self.rtc = rtc

    def begin(self):
        self.buzzer.pulse(.1)
