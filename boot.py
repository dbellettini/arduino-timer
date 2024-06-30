from machine import Pin
from buzzer import Buzzer
b=Buzzer(Pin(21, Pin.OUT))
b.pulse(.1)
