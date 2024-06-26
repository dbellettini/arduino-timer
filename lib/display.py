from machine import Pin
from time import sleep

class Display:
  def __init__(self, rs: Pin, enable: Pin, data: list[Pin]):
    self.rs = rs
    self.enable = enable
    self.data = data
    self.data_len = len(data)
    assert self.data_len in [4, 8], "You need 4 or 8 data pins"
    self.mask = 0xFF >> 8 - len(data)

  def prova(self) -> None:
    self.__write_command(0x01)
    self.__write_command(0x02)
    self.__write_data(int('A'))

  def __write_command(self, value: int) -> None:
    self.rs.value(0)
    self.__write_byte(value)

  def __write_data(self, value: int):
    self.rs.value(1)
    self.__write_byte(value)

  def __pulse_enable(self):
    self.enable.value(0)
    sleep(1e-6)
    self.enable.value(1)
    sleep(1e-6)
    self.enable.value(0)
    sleep(1e-4)

  def __write_byte(self, data: int) -> None:
    if self.data_len == 4:
      self.__write_bits(data >> 4)
    self.__write_bits(data)
  
  def __write_bits(self, data: int) -> None:
    for i, pin in enumerate(self.data):
      pin.value((data >> i) & 0x01)

    self.__pulse_enable()