# Pico-UI-kit
A library to easily work with electronic components using Raspberry Pi Pico

# Getting started
You can download `uikit.py` file and then copy it over to the Pico using e.g. [Thonny](https://github.com/thonny/thonny/). After that you can import it in your code.

When everything is defined in your program, you should call the `run` function, to start the loop which will listen to events in the program, like a buttonpress. This function will block your program until `uikit.quit` is called, so you should put it to the very end of your code.

```python
import uikit

[...]  # define components and functions here

uikit.run()
```

## Button
You can define a pushbutton with the Button class, that will run a Python function when it's pressed. The first argument is the GPIO pin number to which the button is connected. The second argument is the function to run when the button is pressed. With `repeat_interval` you can set, how much time to wait before the button can be pressed again.

```python
import uikit as ui

def func():
    print("Hi!")
    
button = ui.Button(0, func)

# modify on_pressed
button.on_pressed = ui.quit  # will stop the program when the button is pressed

ui.run()
```

## PotentioMeter
A potentiometer to input analog data. You can get its value in the 0-100 range, and it can run a function when its value has changed.

## LCD_16x2
Class to use a 16 by 2, 5x7 character LCD in 8-bit mode. For example: Displaytech 162B
