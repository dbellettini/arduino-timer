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
        self.function_set = FunctionSet()
        self.function_set.set_bits(self.data_len)
        self.display_control = DisplayControl()

    def begin(self, columns: int, lines: int) -> None:
        sleep(0.15)
        self.rs.init(Pin.OUT)
        self.enable.init(Pin.OUT)
        self.rs.value(0)
        self.enable.value(0)

        self.function_set.set_display_lines(lines)
        self.function_set.set_font_type('5x8')

        c = self.function_set.get_command()
        if self.data_len == 4:
            self.__write_bits(0x03)
            sleep(0.0045)
            self.__write_bits(0x03)
            sleep(0.0045)
            self.__write_bits(0x03)
            sleep(0.00015)
            self.__write_bits(0x02)
        else:
            self.__write_command(c)
            sleep(0.0045)
            self.__write_command(c)
            sleep(0.00015)
            self.__write_command(c)

        self.__write_command(c)
        self.__write_command(self.display_control.get_command())

    def test_sentence(self) -> None:
        self.clear()
        self.home()
        self.print("Hello, World!")

    def print(self, text: str) -> None:
        for char in text.encode('ascii'):
            self.__write_data(char)

    def clear(self) -> None:
        self.__write_command(0x01)
        sleep(0.002)

    def home(self):
        self.__write_command(0x02)
        sleep(0.002)

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


class FunctionSet:
    FLAG_BASE = 0x20
    FLAG_8_BIT = 0x10  # DL
    FLAG_2_LINE = 0x08  # N
    FLAG_5x11_DOTS = 0x04  # F

    def __init__(self):
        self.command = self.FLAG_BASE

    def set_bits(self, value: int) -> None:
        assert value in [4, 8], "Must be either 4 or 8 bits"
        if value == 8:
            self.command |= self.FLAG_8_BIT  # Set the 8-bit flag
        else:
            self.command &= ~self.FLAG_8_BIT  # Clear the 8-bit flag

    def set_display_lines(self, lines: int) -> None:
        assert lines in [1, 2], "Must be either 1 or 2 lines"
        if lines == 2:
            self.command |= self.FLAG_2_LINE  # Set the 2-line flag
        else:
            self.command &= ~self.FLAG_2_LINE  # Clear the 2-line flag

    def set_font_type(self, font: str) -> None:
        assert font in ['5x8', '5x11'], "Font must be '5x8' or '5x11'"
        if font == '5x11':
            self.command |= self.FLAG_5x11_DOTS  # Set the 5x11 dots flag
        else:
            self.command &= ~self.FLAG_5x11_DOTS  # Clear the 5x11 dots flag

    def get_command(self) -> int:
        return self.command


class DisplayControl:
    FLAG_BASE = 0x08
    FLAG_DISPLAY_ON = 0x04  # D
    FLAG_CURSOR_ON = 0x02  # C
    FLAG_BLINK_ON = 0x01  # B

    def __init__(self):
        self.command = self.FLAG_BASE | self.FLAG_DISPLAY_ON  # Display on by default

    def set_display(self, value: bool) -> None:
        if value:
            self.command |= self.FLAG_DISPLAY_ON  # Set the display flag
        else:
            self.command &= ~self.FLAG_DISPLAY_ON  # Clear the display flag

    def set_cursor(self, value: bool) -> None:
        if value:
            self.command |= self.FLAG_CURSOR_ON  # Set the cursor flag
        else:
            self.command &= ~self.FLAG_CURSOR_ON  # Clear the cursor flag

    def set_blink(self, value: bool) -> None:
        if value:
            self.command |= self.FLAG_BLINK_ON  # Set the blink flag
        else:
            self.command &= ~self.FLAG_BLINK_ON  # Clear the blink flag

    def get_command(self) -> int:
        return self.command
