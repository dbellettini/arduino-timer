from machine import Pin
from time import sleep


class Display:
    def __init__(self, rs: Pin, enable: Pin, data: list[Pin]):
        self.cursor = None
        self.rs = rs
        self.enable = enable
        self.data = data
        self.data_len = len(data)
        assert self.data_len in [4, 8], "You need 4 or 8 data pins"
        self.mask = 0xFF >> 8 - len(data)
        self.function_set = FunctionSet()
        self.function_set.set_bits(self.data_len)
        self.display_control = DisplayControl()
        self.display_mode = DisplayMode()

    def begin(self, columns: int, lines: int) -> None:
        self.cursor = Cursor(columns, lines)
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
        self.__write_command(self.display_mode.get_command())

    def test_sentence(self) -> None:
        self.clear()
        self.home()
        self.print("Hello, World!")
        self.move_cursor(0, 1)
        self.print("This is a test")

    def print(self, text: str) -> None:
        for char in text.encode('ascii'):
            self.__write_data(char)

    def move_cursor(self, x: int, y: int) -> None:
        self.cursor.move(x, y)

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


class LCDCommand:
    def __init__(self, base_flag: int):
        self.command = base_flag

    def set_flag(self, flag: int, enable: bool) -> None:
        if enable:
            self.command |= flag
        else:
            self.command &= ~flag

    def get_command(self) -> int:
        return self.command


class FunctionSet(LCDCommand):
    FLAG_8_BIT = 0x10  # DL
    FLAG_2_LINE = 0x08  # N
    FLAG_5x11_DOTS = 0x04  # F

    def __init__(self):
        super().__init__(0x20)

    def set_bits(self, value: int) -> None:
        assert value in [4, 8], "Must be either 4 or 8 bits"
        self.set_flag(self.FLAG_8_BIT, value == 8)

    def set_display_lines(self, lines: int) -> None:
        assert lines in [1, 2], "Must be either 1 or 2 lines"
        self.set_flag(self.FLAG_2_LINE, lines == 2)

    def set_font_type(self, font: str) -> None:
        assert font in ['5x8', '5x11'], "Font must be '5x8' or '5x11'"
        self.set_flag(self.FLAG_5x11_DOTS, font == '5x11')


class DisplayControl(LCDCommand):
    FLAG_DISPLAY_ON = 0x04  # D
    FLAG_CURSOR_ON = 0x02  # C
    FLAG_BLINK_ON = 0x01  # B

    def __init__(self):
        super().__init__(0x08)
        self.set_display(True)

    def set_display(self, value: bool) -> None:
        self.set_flag(self.FLAG_DISPLAY_ON, value)

    def set_cursor(self, value: bool) -> None:
        self.set_flag(self.FLAG_CURSOR_ON, value)

    def set_blink(self, value: bool) -> None:
        self.set_flag(self.FLAG_BLINK_ON, value)


class DisplayMode(LCDCommand):
    FLAG_ENTRY_LEFT = 0x02  # I/D
    FLAG_ENTRY_SHIFT = 0x01  # S

    def __init__(self):
        super().__init__(0x04)
        self.set_direction(True)
        self.set_shift(False)

    def set_direction(self, value: bool) -> None:
        self.set_flag(self.FLAG_ENTRY_LEFT, value)

    def set_shift(self, value: bool) -> None:
        self.set_flag(self.FLAG_ENTRY_SHIFT, value)


class Cursor(LCDCommand):
    BASE_FLAG = 0x80

    def __init__(self, columns: int, lines: int):
        super().__init__(self.BASE_FLAG)
        self.columns = columns
        self.lines = lines

    def move(self, x: int, y: int) -> None:
        self.set_flag(0x80 + (y * 0x40) + x, True)
