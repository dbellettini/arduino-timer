from machine import Pin
from buzzer import Buzzer
from display import Display
from progressbar import ProgressBar

b = Buzzer(Pin(21, Pin.OUT))
b.pulse(.1)

d = Display(Pin(18, Pin.OUT), Pin(17, Pin.OUT),
            [Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(5, Pin.OUT)])

d.begin(16, 2)
d.test_sentence()

p = ProgressBar(d, 16, 1)
p.begin()
p.display_progress(0.5)