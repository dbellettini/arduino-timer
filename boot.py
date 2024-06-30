from machine import Pin
from buzzer import Buzzer
from display import Display

b = Buzzer(Pin(21, Pin.OUT))
b.pulse(.1)

d = Display(Pin(18, Pin.OUT), Pin(17, Pin.OUT),
            [Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(5, Pin.OUT)])
d.test_sentence()
