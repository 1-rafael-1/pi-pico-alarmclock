from machine import Pin
class LowPowerManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        self.green_pin=state_mgr.button_green_pin()
        self.blue_pin=state_mgr.button_blue_pin()
        self.yellow_pin=state_mgr.button_yellow_pin()
        self.is_lowpower_mode = False

    def enter_lowpower_mode(self):
        print("Entering lowpower mode...")
        print(f"pins are: {self.green_pin}, {self.blue_pin}, {self.yellow_pin}")
        self.state_mgr.deinit()
        self.init_buttons()
        self.toggle_clock_speed()
        self.is_lowpower_mode = True

    def exit_lowpower_mode(self):
        print("Exiting lowpower mode...")
        self.toggle_clock_speed()
        self.deinit_buttons()
        self.state_mgr.initialize()
        self.is_lowpower_mode = False

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
            self.state_mgr.set_high_clock_speed()