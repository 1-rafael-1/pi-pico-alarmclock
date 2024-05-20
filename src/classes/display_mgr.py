#inspiration from https://blog.martinfitzpatrick.com/displaying-images-oled-displays/

import micropython
from gc import collect, mem_free
from machine import I2C, Pin, RTC, Timer
from utime import sleep
import framebuf
import drivers.ssd1306 as ssd1306

@micropython.native
class DisplayManager:
    def __init__(self, state_mgr, width=128, height=64):
        self.state_mgr = state_mgr
        self.i2c = I2C(0, scl=Pin(13), sda=Pin(12)) 
        self.display = ssd1306.SSD1306_I2C(width, height, self.i2c)
        self.display.contrast(10) # to save power, 255 is default
        self.update_display_timer = None
        self.blinking_set_alarm_time = False
        self.blinking_set_alarm_time_timer = None
        self.blinking_set_alarm_time_showing = False
        self.boot_messages = []

        
    def initialize(self):
        self.power_on()

    def initialize_normal_operation(self):
        self.clear()
        self.compose()

    def start_update_display_timer(self):
        if self.update_display_timer is None:
            self.state_mgr.log_emit("Starting update display timer", self.__class__.__name__)
            self.update_display_timer = Timer(period=60000, mode=Timer.PERIODIC, callback=lambda t: self.compose())

    def stop_update_display_timer(self):
        if self.update_display_timer is not None:
            self.state_mgr.log_emit("Stopping update display timer", self.__class__.__name__)
            self.update_display_timer.deinit()
            self.update_display_timer = None

    def start_blinking_set_alarm_time(self):
        self.blinking_set_alarm_time = True
        if self.blinking_set_alarm_time_timer is None:
            self.state_mgr.log_emit("Starting blinking set alarm time timer", self.__class__.__name__)
            self.blinking_set_alarm_time_timer = Timer(period=300, mode=Timer.PERIODIC, callback=lambda t: self.blink_alarm_time())

    def stop_blinking_set_alarm_time(self):
        self.blinking_set_alarm_time = False
        if self.blinking_set_alarm_time_timer is not None:
            self.state_mgr.log_emit("Stopping blinking set alarm time timer", self.__class__.__name__)
            self.blinking_set_alarm_time_timer.deinit()
            self.blinking_set_alarm_time_timer = None
    
    @micropython.native
    def blink_alarm_time(self):
        if self.blinking_set_alarm_time_showing:
            self.clear_content_area()
            self.blinking_set_alarm_time_showing = False
        else:
            self.display_alarm_time()
            self.blinking_set_alarm_time_showing = True

    @micropython.native
    def clear(self):
        self.display.fill(0)
        self.display.show()

    @micropython.native
    def display_text(self, text, x=0, y=0):
        self.display.text(text, x, y)

    def power_on(self):
        self.display.poweron()
    
    def power_off(self):
        self.clear()
        self.display.poweroff()

    @micropython.native
    def load_image(self, file):
        with open(file, 'rb') as f:
            f.readline()  # Magic number
            f.readline()  # Creator comment
            f.readline()  # Dimensions
            data = bytearray(f.read())
        return data

    @micropython.native
    def display_battery_state(self):
        self.state_mgr.power_read_vsys()
        mains_powered = self.state_mgr.power_is_usb_powered()
        if not mains_powered:
            battery_percentage = self.state_mgr.power_get_battery_charge_percentage()
        if mains_powered: file = 'media/bat_mains.pbm'
        elif battery_percentage >=80: file = 'media/bat_100.pbm'
        elif battery_percentage >=60 and battery_percentage <80: file = 'media/bat_080.pbm'
        elif battery_percentage >=40 and battery_percentage <60: file = 'media/bat_060.pbm'
        elif battery_percentage >=20 and battery_percentage <40: file = 'media/bat_040.pbm'
        elif battery_percentage >0 and battery_percentage<20: file = 'media/bat_020.pbm'
        else: file = 'media/bat_000.pbm'

        data = self.load_image(file)
        fbuf = framebuf.FrameBuffer(data, 20, 11, framebuf.MONO_HLSB)
        self.display.blit(fbuf, 108, 0)
        self.display.show()

    def get_time(self):
        # Get the current time
        rtc = RTC()
        return '{:02d}:{:02d}'.format(rtc.datetime()[4], rtc.datetime()[5])
    
    @micropython.native
    def display_time(self, time):
        # Split the time into hours and minutes
        hours, minutes = time.split(':')
    
        # Define the starting position
        x = 13
        y = 26
    
        # For each digit in the time, draw it on the display
        for i, digit in enumerate(hours + ':' + minutes):
            if digit == ':':
                file = 'media/colon.pbm'
                width = 10
            else:
                file = f'media/{digit}.pbm'
                width = 23
            height = 24
    
            data = self.load_image(file)
            fbuf = framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)
            self.display.blit(fbuf, x, y)
            x += width + 1
    
        self.display.show()

    @micropython.native
    def clear_content_area(self):
        self.display.fill_rect(0, 14, 128, 64-14, 0) # x start, y start, width, height        
        self.display.show()

    @micropython.native
    def display_state_region(self):
        if self.state_mgr.is_menu_active(): #menu beats alarm
            file = 'media/settings.pbm'
            data = self.load_image(file)
        elif self.state_mgr.alarm_active: #alarm beats idle
            file = 'media/saber.pbm'
            data = self.load_image(file)
        else: #neither menu nor alarm active
            data = bytearray(100 * 16)
        
        fbuf = framebuf.FrameBuffer(data, 100, 16, framebuf.MONO_HLSB)
        self.display.blit(fbuf, 1, 1)
        self.display.show()
        
    @micropython.native
    def display_input_voltage(self):
        self.state_mgr.power_read_vsys()
        voltage = round(self.state_mgr.power_get_vsys_voltage(),2)
        self.display_text(f'Vsys: {voltage}V', 0, 17)
        self.display.show()

    @micropython.native
    def display_available_memory(self):
        collect()
        available_memory = mem_free() / 1024
        self.display.text(f'Mem. free: {available_memory} kb', 0, 33)
        self.display.show()

    @micropython.native
    def display_board_temperature(self):
        self.state_mgr.power_read_temperature()
        temperature = self.state_mgr.power_get_temperature()
        self.display.text(f'B-Temp.: {temperature}C', 0, 49)
        self.display.show()

    @micropython.native
    def display_system_select(self):
        self.display.text('GREEN: shut down', 0, 17)
        self.display.text('BLUE: info', 0, 33)
        self.display.text('YELLOW: resume', 0, 49)
        self.display.show()

    @micropython.native
    def display_shutdown(self):
        self.display.text('Powering down...', 0, 33)
        self.display.show()

    @micropython.native
    def compose(self):
        if self.state_mgr.menu_get_state() in ['idle', 'alarm_raised']:
            self.display_time(self.get_time())
        elif self.state_mgr.menu_get_state() == 'system':
            self.clear_content_area()
            if self.state_mgr.menu_get_system_state() == 'select':
                self.state_mgr.log_emit("Displaying system select", self.__class__.__name__)
                self.display_system_select()
            elif self.state_mgr.menu_get_system_state() == 'info':
                self.state_mgr.log_emit("Displaying system info", self.__class__.__name__)
                self.display_input_voltage()
                self.display_available_memory()
                self.display_board_temperature()
            elif self.state_mgr.menu_get_system_state() == 'shutdown':
                self.state_mgr.log_emit("Displaying system shutdown", self.__class__.__name__)
                self.display_shutdown()
        if not self.state_mgr.alarm_is_alarm_raised():
            self.display_battery_state()
            self.display_state_region()

    @micropython.native
    def compose_boot(self, message):
        self.clear()
        self.display_text('Booting...', 0, 0)
        
        self.boot_messages.append(message)
    
        for i, message in enumerate(self.boot_messages[-3:], start=1):
            self.display_text(message, 0, i*16)
    
        self.display.show()

    @micropython.native
    def display_alarm_time(self):
        self.display_time(self.state_mgr.alarm_time)

    @micropython.native
    def display_alarm_quit_sequence(self, index):
        if index < 0 or index >= len(self.state_mgr.alarm_quit_button_sequence()):
            return
        # Clear the state area and the battery area
        self.clear_first_row()
        # Display the text from state_mgr.alarm_quit_button_sequence at the given index
        sequence_text = self.state_mgr.alarm_quit_button_sequence()[index]
        self.display.text(sequence_text, 0, 0)
        self.display.show()

    @micropython.native
    def clear_first_row(self):
        self.display.fill_rect(0, 0, 128, 16, 0)
        self.display.show()
        
    def deinit(self):
        self.stop_update_display_timer()
        self.stop_blinking_set_alarm_time()
        self.power_off()

## Mocks for testing
# use to test DisplayManager in isolation
class MockStateManager:
    def __init__(self):
        self.alarm_time = "00:00"
        self.alarm_active = False
        self.menu_active = False
        self.setting_alarm_hours = False
        self.setting_alarm_minutes = False
        self.menu_system_state = 'info'

    def get_time(self):
        return "12:00"
    
    def set_alarm_active(self, value):
        self.alarm_active = value

    def set_menu_is_active(self, value):
        self.menu_active = value

    def set_alarm_time(self, time):
        self.alarm_time = time

    def get_battery_voltage(self):
        return 3.7

    def get_battery_percentage(self):
        return 50

    def is_charging(self):
        return False

    def is_alarm_active(self):
        return self.alarm_active

    def is_menu_active(self):
        return self.menu_active

    def is_setting_alarm_hours(self):
        return self.setting_alarm_hours

    def is_setting_alarm_minutes(self):
        return self.setting_alarm_minutes
    
    def read_vsys(self):
        pass

    def is_usb_powered(self):
        return False
    
    def get_battery_charge_percentage(self):
        return 50
    
    def get_vsys_voltage(self):
        return 3.7
    
    def alarm_quit_button_sequence(self):
        return ['green', 'blue', 'yellow']
    
    def menu_get_state(self):
        if self.menu_active:
            return 'system'
        if self.alarm_active:
            return 'alarm_raised'
        return 'idle'
    
    def power_read_vsys(self):
        pass

    def power_is_usb_powered(self):
        return False
    
    def power_get_battery_charge_percentage(self):
        return 50
    
    def alarm_is_alarm_raised(self):
        return False
    
    def power_get_vsys_voltage(self):
        return 3.7
    
    def set_menu_system_state(self, state):
        self.menu_system_state = state

    def menu_get_system_state(self):
        return self.menu_system_state

## Tests
def display_manager_composes():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager compose")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager composes
    display_mgr.compose()
    #[THEN]: DisplayManager composes successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_alarm_time():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager display alarm time")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager displays alarm time
    display_mgr.display_alarm_time()
    #[THEN]: DisplayManager displays alarm time successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_input_voltage():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager display input voltage")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager displays input voltage
    display_mgr.display_input_voltage()
    #[THEN]: DisplayManager displays input voltage successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_state_region():
    #[GIVEN]: DisplayManager instance, alarm active
    print("Test DisplayManager display state region")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    state_mgr.set_alarm_active(True)
    #[WHEN]: DisplayManager displays state region
    display_mgr.display_state_region()
    #[THEN]: DisplayManager displays state region successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_battery_state():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager display battery state")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager displays battery state
    display_mgr.display_battery_state()
    #[THEN]: DisplayManager displays battery state successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_alarm_quit_sequence():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager display alarm quit sequence")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager displays first part of alarm quit sequence
    display_mgr.display_alarm_quit_sequence(0)
    #[THEN]: DisplayManager displays alarm quit sequence successfully
    sleep(1)
    #[WHEN]: DisplayManager displays second part of alarm quit sequence
    display_mgr.display_alarm_quit_sequence(1)
    #[THEN]: DisplayManager displays alarm quit sequence successfully
    sleep(1)
    #[WHEN]: DisplayManager displays third part of alarm quit sequence
    display_mgr.display_alarm_quit_sequence(2)
    #[THEN]: DisplayManager displays alarm quit sequence successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_shutdown_after_normal_display():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager display shutdown")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[GIVEN]: Menu system state is 'select', we are in menu state 'idle' 
    state_mgr.set_menu_system_state('select')
    state_mgr.set_menu_is_active(False)
    #[WHEN]: DisplayManager composes
    display_mgr.compose()
    #[THEN]: DisplayManager composes successfully
    sleep(1)
    #[WHEN]: we have progressed to menu state 'system' and system state 'shutdown'
    state_mgr.set_menu_system_state('shutdown')
    state_mgr.set_menu_is_active(True)
    #[WHEN]: DisplayManager displays shutdown message
    display_mgr.compose()
    display_mgr.display_shutdown()
    #[THEN]: DisplayManager displays shutdown message successfully
    sleep(1)
    #[TEARDOWN]
    display_mgr.deinit()

def display_manager_displays_system_select():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager display system select")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[GIVEN]: Menu system state is 'select', we are in menu state 'idle' 
    state_mgr.set_menu_system_state('select')
    state_mgr.set_menu_is_active(False)
    #[WHEN]: DisplayManager composes
    display_mgr.compose()
    #[THEN]: DisplayManager composes successfully
    sleep(1)
    #[WHEN]: we have progressed to menu state 'system' and system state 'select'
    state_mgr.set_menu_system_state('select')
    state_mgr.set_menu_is_active(True)
    #[WHEN]: DisplayManager composes
    display_mgr.compose()
    #[THEN]: DisplayManager composes successfully
    sleep(3)
    #[TEARDOWN]
    display_mgr.deinit()

def display_iterate_contrast():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager iterate contrast")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager iterates contrast
    for i in range(0, 255, 10):
        display_mgr.display.contrast(i)
        display_mgr.compose()
        sleep(1)
        print("Contrast: ", i)
    #[THEN]: DisplayManager iterates contrast successfully
    #[TEARDOWN]
    display_mgr.deinit()

def display_clears_content_area():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager clear content area")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: 4 lines of text are displayed
    display_mgr.display_text('Line 1', 0, 0)
    display_mgr.display_text('Line 2', 0, 16)
    display_mgr.display_text('Line 3', 0, 32)
    display_mgr.display_text('Line 4', 0, 48)
    display_mgr.display.show()
    #[THEN]: 4 lines of text are displayed successfully
    sleep(3)
    #[WHEN]: DisplayManager clears first row
    display_mgr.clear_first_row()
    #[THEN]: DisplayManager clears first row successfully
    sleep(3)
    #[WHEN]: DisplayManager clears content area
    display_mgr.clear_content_area()
    #[THEN]: DisplayManager clears content area successfully
    sleep(3)
    #[TEARDOWN]
    display_mgr.deinit()

def display_composes_boot():
    #[GIVEN]: DisplayManager instance
    print("Test DisplayManager compose boot")
    state_mgr = MockStateManager()
    display_mgr = DisplayManager(state_mgr)
    #[WHEN]: DisplayManager composes boot
    for i in range(1, 7):
        display_mgr.compose_boot(f'Message {i}')
        sleep(1)
    #[THEN]: DisplayManager composes boot successfully
    sleep(3)
    #[TEARDOWN]
    display_mgr.deinit()