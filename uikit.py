import time
from machine import ADC, Pin

running = True
elements_with_events = []
on_quit = []


class LCDCommands:
    BlinkOff = 0xE
    BlinkOn = 0xF
    ClearDisplay = 0x1
    HideCursor = 0xC
    CursorOff = 0xC
    CursorOn = 0xF
    ShowCursor = 0xE
    EntryMode = 0x6
    Font5x7 = 0x38
    MoveHome = 0x2
    InitDisplay = 0xF
    MoveLeft = 0x10
    MoveRight = 0x14
    ScrollLeft = 0x18
    ScrollRight = 0x1C
    TurnOff = 0x8
    TurnOn = 0xF


class Button:
    """A button that runs a function when the it's pressed."""

    def __init__(
        self, pin: int, callback: "callable" = None, repeat_interval: float = 0.1
    ) -> None:
        self._pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)

        self.pressed = bool(self._pin.value)
        self.on_pressed = callback
        self.repeat_interval = repeat_interval

        elements_with_events.append(self)

    def _handle_events(self) -> None:
        if self._pin.value():
            if not self.pressed:
                self.pressed = True
                if self.on_pressed is not None:
                    self.on_pressed()
        else:
            self.pressed = False
            time.sleep(self.repeat_interval)


class PotentioMeter:
    """
    A potentiometer to input analog data.
    You can get its value in the 0-100 range, and it can run a function when its value has changed.
    """

    def __init__(self, pin: int, callback: "callable" = None) -> None:
        self._adc = ADC(Pin(pin))

        self._value = self.value
        self.on_changed = callback

        elements_with_events.append(self)

    @property
    def value(self) -> float:
        return round(self._adc.read_u16() / 65535, 2) * 100

    def _handle_events(self) -> None:
        new_value = self.value

        if new_value != self._value and self.on_changed is not None:
            self.on_changed()

        self._value = new_value


class LCD_16x2:
    """
    Class to use a 16 by 2, 5x7 character LCD in 8-bit mode.
    For example: Displaytech 162B
    """

    def __init__(
        self, text: str = None, *, pins: list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    ) -> None:
        self._cur_pos = 1

        self._pin_7 = Pin(pins[0], Pin.OUT)
        self._pin_6 = Pin(pins[1], Pin.OUT)
        self._pin_5 = Pin(pins[2], Pin.OUT)
        self._pin_4 = Pin(pins[3], Pin.OUT)
        self._pin_3 = Pin(pins[4], Pin.OUT)
        self._pin_2 = Pin(pins[5], Pin.OUT)
        self._pin_1 = Pin(pins[6], Pin.OUT)
        self._pin_0 = Pin(pins[7], Pin.OUT)

        self._enable_pin = Pin(pins[8], Pin.OUT, value=0)
        self._register_pin = Pin(pins[9], Pin.OUT, value=0)

        self.send_command(LCDCommands.Font5x7)
        self.send_command(LCDCommands.InitDisplay)
        self.send_command(LCDCommands.EntryMode)
        self.send_command(LCDCommands.ClearDisplay)

        on_quit.append(self._fulloff)

        if text is not None:
            self.write(text)

    def _register_command(self) -> None:
        self._register_pin.low()

    def _register_data(self) -> None:
        self._register_pin.high()

    def _enable(self) -> None:
        self._enable_pin.high()
        time.sleep(0.004)
        self._enable_pin.low()

    def _fulloff(self):
        self.clear()
        self.off()

    def send_command(self, command: int) -> None:
        self._register_command()

        bits = "{0:08b}".format(command)

        self._pin_7.value(int(bits[0]))
        self._pin_6.value(int(bits[1]))
        self._pin_5.value(int(bits[2]))
        self._pin_4.value(int(bits[3]))
        self._pin_3.value(int(bits[4]))
        self._pin_2.value(int(bits[5]))
        self._pin_1.value(int(bits[6]))
        self._pin_0.value(int(bits[7]))

        self._enable()

    def send_data(self, data: int) -> None:
        self._register_data()

        bits = "{0:08b}".format(data)

        self._pin_7.value(int(bits[0]))
        self._pin_6.value(int(bits[1]))
        self._pin_5.value(int(bits[2]))
        self._pin_4.value(int(bits[3]))
        self._pin_3.value(int(bits[4]))
        self._pin_2.value(int(bits[5]))
        self._pin_1.value(int(bits[6]))
        self._pin_0.value(int(bits[7]))

        self._enable()

    def write(self, text) -> None:
        for char in str(text):
            self._cur_pos += 1
            self.send_data(ord(char))

    def move_cursor(self, value: int = 1) -> None:
        if value == 0:
            return

        for _ in range(abs(value)):
            if value > 0:
                self.send_command(LCDCommands.MoveRight)
            else:
                self.send_command(LCDCommands.MoveLeft)
        self._cur_pos += value

    def on(self) -> None:
        self.send_command(LCDCommands.TurnOn)

    def off(self) -> None:
        self.send_command(LCDCommands.TurnOff)

    def clear(self) -> None:
        self._cur_pos = 1
        self.send_command(LCDCommands.ClearDisplay)

    def home(self) -> None:
        self._cur_pos = 1
        self.send_command(LCDCommands.MoveHome)

    def cursor_on(self) -> None:
        self.send_command(LCDCommands.CursorOn)

    def cursor_off(self) -> None:
        self.send_command(LCDCommands.CursorOff)

    def show_cursor(self) -> None:
        self.send_command(LCDCommands.ShowCursor)

    def hide_cursor(self) -> None:
        self.send_command(LCDCommands.HideCursor)

    def blink_on(self) -> None:
        self.send_command(LCDCommands.BlinkOn)

    def blink_off(self) -> None:
        self.send_command(LCDCommands.BlinkOff)

    def scroll_right(self) -> None:
        self.send_command(LCDCommands.ScrollRight)

    def scroll_left(self) -> None:
        self.send_command(LCDCommands.ScrollLeft)

    def new_line(self) -> None:
        for _ in range(41 - self._cur_pos):
            self.send_command(LCDCommands.MoveRight)


def quit():
    global running
    for func in on_quit:
        func()
    running = False


def run():
    while running:
        for item in elements_with_events:
            item._handle_events()
