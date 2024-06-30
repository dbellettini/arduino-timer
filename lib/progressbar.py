from display import Display


def create_block_pattern(filled_bits: int):
    return 0b11111 << (5 - filled_bits)


class ProgressBar:
    def __init__(self, display: Display, columns: int, row: int):
        self.display = display
        self.columns = columns
        self.row = row

    def begin(self):
        self.__create_custom_characters()

    def display_progress(self, rate: float):
        self.display.move_cursor(0, self.row)
        total_blocks = self.columns * 5
        progress = int(round(rate * total_blocks))

        for i in range(self.columns):
            size = min(progress, 5)
            self.display.print_char(size)
            progress -= size

    def __create_custom_characters(self):
        for i in range(6):
            self.display.create_char(i, [create_block_pattern(i)] * 8)
