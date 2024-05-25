import micropython
from machine import Pin
from utime import ticks_ms, sleep_ms

class ButtonManager:
    def __init__(self, state_mgr, green_pin=20, blue_pin=21, yellow_pin=22, debounce_time=300):
        self.state_mgr = state_mgr
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.yellow_pin = yellow_pin
        self.green_button = Pin(green_pin, Pin.IN, Pin.PULL_UP)
        self.blue_button = Pin(blue_pin, Pin.IN, Pin.PULL_UP)
        self.yellow_button = Pin(yellow_pin, Pin.IN, Pin.PULL_UP)
        self.button_presses = {"green": 0, "blue": 0, "yellow": 0}
        self.last_time = {"green": 0, "blue": 0, "yellow": 0}
        self.debounce_time = debounce_time
        
    def initialize(self):
        self.setup_interrupts()

    def setup_interrupts(self):
        self.green_button.irq(trigger=self.green_button.IRQ_RISING, handler=self.button_callback)
        self.blue_button.irq(trigger=self.blue_button.IRQ_RISING, handler=self.button_callback)
        self.yellow_button.irq(trigger=self.yellow_button.IRQ_RISING, handler=self.button_callback)

    def disable_interrupts(self):
        self.green_button.irq(trigger=0)
        self.blue_button.irq(trigger=0)
        self.yellow_button.irq(trigger=0)

    def get_green_pin(self):
        return self.green_pin
    
    def get_blue_pin(self):
        return self.blue_pin
    
    def get_yellow_pin(self):
        return self.yellow_pin
    
    def get_green_button(self):
        return self.green_button
    
    def get_blue_button(self):
        return self.blue_button
    
    def get_yellow_button(self):
        return self.yellow_button
    
    @micropython.native
    def button_callback(self, pin):
        from utime import ticks_ms
        new_time_pressed = ticks_ms()
        if pin == self.green_button:
            button = "green"
        elif pin == self.blue_button:
            button = "blue"
        elif pin == self.yellow_button:
            button = "yellow"
        else:
            return
        self.state_mgr.log_emit("Button pressed: " + button, self.__class__.__name__)
        if self.is_new_event(button, new_time_pressed):
            if button == "green":
                self.state_mgr.menu_press_green_button()
            elif button == "blue":
                self.state_mgr.menu_press_blue_button()
            elif button == "yellow":
                self.state_mgr.menu_press_yellow_button()

    @micropython.native
    def is_new_event(self, button, new_time_pressed):
        if (new_time_pressed - self.last_time[button]) > self.debounce_time:
            self.last_time[button] = new_time_pressed
            return True
        return False
    
    def deinit(self):
        self.disable_interrupts()

## Mocks for testing
# use to test ButtonManager in isolation

class MockStateManager:
    def __init__(self):
        self.green_button_presses = 0
        self.blue_button_presses = 0
        self.yellow_button_presses = 0
        self.log = []
    
    def log_emit(self, message, source):
        self.log.append(message)
    
    def menu_press_green_button(self):
        self.green_button_presses += 1
    
    def menu_press_blue_button(self):
        self.blue_button_presses += 1
    
    def menu_press_yellow_button(self):
        self.yellow_button_presses += 1

    def log_emit(self, message, source_class):
        print(message)


## Tests

def button_manager_runs():
    #[GIVEN]: ButtonManager instance
    state_mgr = MockStateManager()
    button_mgr = ButtonManager(state_mgr)
    #[WHEN]: initialize
    button_mgr.initialize()
    #[THEN]: button presses are 0
    assert state_mgr.green_button_presses == 0, "Expected green button presses to be 0"
    assert state_mgr.blue_button_presses == 0, "Expected blue button presses to be 0"
    assert state_mgr.yellow_button_presses == 0, "Expected yellow button presses to be 0"
    #[WHEN]: button presses
    button_mgr.button_callback(button_mgr.get_green_button())
    button_mgr.button_callback(button_mgr.get_blue_button())
    button_mgr.button_callback(button_mgr.get_yellow_button())
    #[THEN]: button presses are 1
    assert state_mgr.green_button_presses == 1, "Expected green button presses to be 1"
    assert state_mgr.blue_button_presses == 1, "Expected blue button presses to be 1"
    assert state_mgr.yellow_button_presses == 1, "Expected yellow button presses to be 1"
    #[TEARDOWN]
    button_mgr.deinit()