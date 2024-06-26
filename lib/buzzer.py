from machine import Pin
from time import sleep

class Buzzer:
  def __init__(self, pin: Pin):
    self.pin = pin

  def pulse(self, length: float) -> None:
    self.pin.value(1)
    sleep(length)
    self.pin.value(0)

  def alarm(self) -> None:
    for j in range(4):
      for i in range(4):
        self.pulse(.1)
        sleep(.1)
      sleep(.4)
