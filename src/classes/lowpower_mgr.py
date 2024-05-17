from machine import Pin
from utime import sleep
class LowPowerManager:
    def __init__(self, state_mgr, green_pin=20, blue_pin=21, yellow_pin=22):
        self.state_mgr = state_mgr
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.yellow_pin = yellow_pin
        self.is_lowpower_mode = False

    def enter_lowpower_mode(self):
        print("Entering lowpower mode...")
        print(f"pins are: {self.green_pin}, {self.blue_pin}, {self.yellow_pin}")
        self.is_lowpower_mode = True
        self.state_mgr.deinit()
        sleep(1)
        self.init_buttons()
        sleep(1)
        self.toggle_clock_speed()

    def exit_lowpower_mode(self):
        print("Exiting lowpower mode...")
        self.is_lowpower_mode = False
        self.toggle_clock_speed()
        self.deinit_buttons()
        sleep(1)
        self.state_mgr.initialize()

    def button_callback(self, pin):
        if self.is_lowpower_mode:
            self.exit_lowpower_mode()

    def init_buttons(self):
        self.green_button = Pin(self.green_pin, Pin.IN, Pin.PULL_UP)
        self.blue_button = Pin(self.blue_pin, Pin.IN, Pin.PULL_UP)
        self.yellow_button = Pin(self.yellow_pin, Pin.IN, Pin.PULL_UP)
        self.green_button.irq(trigger=self.green_button.IRQ_RISING, handler=self.button_callback)
        self.blue_button.irq(trigger=self.blue_button.IRQ_RISING, handler=self.button_callback)
        self.yellow_button.irq(trigger=self.yellow_button.IRQ_RISING, handler=self.button_callback)

    def deinit_buttons(self):
        self.green_button.irq(handler=None)
        self.blue_button.irq(handler=None)
        self.yellow_button.irq(handler=None)
        self.green_button = None
        self.blue_button = None
        self.yellow_button = None

    def toggle_clock_speed(self):
        if self.is_lowpower_mode:
            self.state_mgr.set_low_clock_speed()
        else:
            self.state_mgr.set_full_clock_speed()

    def is_lowpower_mode_active(self):
        return self.is_lowpower_mode