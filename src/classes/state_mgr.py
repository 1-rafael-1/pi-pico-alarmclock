import json
import _thread
from utime import sleep
from machine import freq
from classes.wifi_mgr import WifiManager
from classes.neopixel_mgr import NeoPixelManager
from classes.display_mgr import DisplayManager
from classes.time_mgr import TimeManager
from classes.sound_mgr import SoundManager
from classes.btn_mgr import ButtonManager
from classes.menu_mgr import MenuManager
from classes.power_mgr import PowerManager
from classes.alarm_mgr import AlarmManager
from classes.lowpower_mgr import LowPowerManager

class StateManager:
    def __init__(self):
        self.button_green_pin = 20
        self.button_blue_pin = 21
        self.button_yellow_pin = 22
        self.power_manager = PowerManager()
        self.wifi_manager = WifiManager()
        self.time_manager = TimeManager(self)
        self.neopixel_manager = NeoPixelManager(self)
        self.display_manager = DisplayManager(self)
        self.menu_manager = MenuManager(self)
        self.button_manager = ButtonManager(self, green_pin=self.button_green_pin, blue_pin=self.button_blue_pin, yellow_pin=self.button_yellow_pin)
        self.sound_manager = SoundManager(self)
        self.alarm_manager = AlarmManager(self)
        self.lowpower_manager = LowPowerManager(self, green_pin=self.button_green_pin, blue_pin=self.button_blue_pin, yellow_pin=self.button_yellow_pin)
        self.alarm_active = False
        self.menu_active = False
        self.alarm_time = '{:02d}:{:02d}'.format(0,0)
        self.alarm_raised = False
        self.lock = _thread.allocate_lock()

    def initialize(self):
        self.set_full_clock_speed()

        self.power_manager.initialize()

        self.time_manager.initialize()
        self.time_manager.start_update_rtc_timer()

        self.read_alarm_time()
        self.read_alarm_active()

        self.display_manager.initialize()
        self.display_manager.start_update_display_timer()

        self.neopixel_manager.initialize()
        if not self.is_alarm_active():
            self.neopixel_manager.start_update_analog_clock_timer()
        else:
            self.set_reduced_clock_speed()

        self.button_manager.initialize()

        self.alarm_manager.start_alarm_timer()

    # region global state methods
    def set_alarm_active(self, value):
        self.alarm_active = value
        self.write_alarm_active()
        print('Alarm active:', self.alarm_active)

    def is_alarm_active(self):
        return self.alarm_active
    
    def set_menu_is_active(self, value):
        self.menu_active = value

    def is_menu_active(self):
        return self.menu_active
    
    def set_alarm_time(self, time):
        self.alarm_time = time
    
    def get_alarm_time(self):
        return self.alarm_time

    def read_alarm_time(self):
        with open('settings//alarm.json', 'r') as file:
            data = json.load(file)
            self.alarm_time = data['alarm_time']

    def write_alarm_time(self):
        with open('settings//alarm.json', 'r') as file:
            data = json.load(file)
        data['alarm_time'] = self.alarm_time
        with open('settings//alarm.json', 'w') as file:
            json.dump(data, file)
        print('Alarm time:', self.alarm_time)       

    def read_alarm_active(self):
        with open('settings//alarm.json', 'r') as file:
            data = json.load(file)
            self.alarm_active = data['alarm_active']

    def write_alarm_active(self):
        with open('settings//alarm.json', 'r') as file:
            data = json.load(file)
        data['alarm_active'] = self.alarm_active
        with open('settings//alarm.json', 'w') as file:
            json.dump(data, file)

    def set_full_clock_speed(self):
        freq(125000000) # 125 MHz, default clock speed for RP2040
        sleep(1) # wait for clock speed to stabilize
        print(f"Clock speed set to: {freq()}")

    def set_reduced_clock_speed(self):
        freq(80000000)
        sleep(1) # wait for clock speed to stabilize
        print(f"Clock speed set to: {freq()}")

    def set_low_clock_speed(self):
        freq(20000000) # 20 MHz, lowest clock speed for RP2040
        sleep(1) # wait for clock speed to stabilize
        print(f"Clock speed set to: {freq()}")
    # endregion

    # region PowerManager methods
    def power_get_battery_state(self):
        return self.power_manager.get_battery_state()
    
    def power_get_battery_charge_percentage(self):
        return self.power_manager.get_battery_charge_percentage()
    
    def power_is_usb_powered(self):
        return self.power_manager.is_usb_powered()
    
    def power_read_vsys(self):
        self.power_manager.read_vsys()

    def power_get_vsys_voltage(self):
        return self.power_manager.vsys_voltage
    
    def power_read_temperature(self):
        self.power_manager.read_temperature()

    def power_get_temperature(self):
        return self.power_manager.get_temperature()
    # endregion

    # region WifiManager methods
    def wifi_connect_wifi(self, max_wait=20, indicator=True):
        self.wifi_manager.connect(max_wait=20, indicator=True)

    def wifi_disconnect_wifi(self, max_wait=20, indicator=True):
        self.wifi_manager.disconnect(max_wait=20, indicator=True)

    def wifi_reconnect_wifi(self, max_wait=20):
        self.wifi_manager.reconnect(max_wait=20)

    def wifi_is_network_up(self):
        return self.wifi_manager.is_network_up()
    # endregion

    # region MenuManager methods
    def menu_press_green_button(self):
        self.menu_manager.press_green_button()

    def menu_press_blue_button(self):
        self.menu_manager.press_blue_button()

    def menu_press_yellow_button(self):
        self.menu_manager.press_yellow_button()

    def menu_set_state(self, state):
        self.menu_manager.set_state(state)

    def menu_get_state(self):
        return self.menu_manager.get_state()
    
    def menu_get_system_state(self):
        return self.menu_manager.get_system_state()
    # endregion

    # region DisplayManager methods
    def display_clear(self):
        self.display_manager.clear()

    def display_compose(self):
        self.display_manager.compose()

    def display_state_region(self):
        self.display_manager.display_state_region()

    def display_display_battery_state(self):
        self.display_manager.display_battery_state()

    def display_start_update_display_timer(self):
        self.display_manager.start_update_display_timer()

    def display_stop_update_display_timer(self):
        self.display_manager.stop_update_display_timer()

    def display_time(self, time):
        self.display_manager.display_time(time)

    def display_start_blinking_set_alarm_time(self):
        self.display_manager.start_blinking_set_alarm_time()

    def display_stop_blinking_set_alarm_time(self):
        self.display_manager.stop_blinking_set_alarm_time()

    def display_clear_first_row(self):
        self.display_manager.clear_first_row()

    def display_alarm_quit_sequence(self, index):
        self.display_manager.display_alarm_quit_sequence(index)
    # endregion

    # region NeoPixelManager methods
    def neopixel_all_off(self):
        self.neopixel_manager.all_off()

    def neopixel_get_color(self, red, green, blue):
        return self.neopixel_manager.get_color(red, green, blue)
    
    def neopixel_pendulum(self, colors, delay, loops):
        self.neopixel_manager.pendulum(colors, delay, loops)

    def neopixel_chase(self, colors, delay, loops):
        self.neopixel_manager.chase(colors, delay, loops)

    def neopixel_turning_wheel(self, colors, delay, loops):
        self.neopixel_manager.turning_wheel(colors, delay, loops)

    def neopixel_sunrise(self, duration):
        self.neopixel_manager.sunrise(duration)

    def neopixel_start_update_analog_clock_timer(self):
        self.neopixel_manager.start_update_analog_clock_timer()

    def neopixel_stop_update_analog_clock_timer(self):
        self.neopixel_manager.stop_update_analog_clock_timer()
    # endregion

    # region AlarmManager methods
    def alarm_start_alarm_timer(self):
        self.alarm_manager.start_alarm_timer()

    def alarm_stop_alarm_timer(self):
        self.alarm_manager.stop_alarm_timer()

    def alarm_set_alarm_raised(self, value):
        self.alarm_raised = value

    def alarm_is_alarm_raised(self):
        with self.lock:
            return self.alarm_raised

    def alarm_quit_button_sequence(self):
        return self.alarm_manager.alarm_quit_button_sequence
    
    def alarm_remove_first_quit_button_sequence(self):
        self.alarm_manager.remove_first_quit_button_sequence()

    def alarm_quit_alarm(self):
        self.alarm_manager.quit_alarm()

    def alarm_clear_last_alarm_stopped_time(self):
        self.alarm_manager.clear_last_alarm_stopped_time()
 
    def alarm_start_alarm_sequence_thread(self):
        self.alarm_manager.start_alarm_sequence_thread()
    # endregion

    # region SoundManager methods
    def sound_alarm_sequence(self):
        self.sound_manager.alarm_sequence()

    def sound_alarm_stop(self):
        self.sound_manager.alarm_stop()
    # endregion

    # region LowPowerManager methods
    def lowpower_enter_lowpower_mode(self):
        self.lowpower_manager.enter_lowpower_mode()

    def lowpower_is_lowpower_mode_active(self):
        return self.lowpower_manager.is_lowpower_mode_active()
    # endregion

    # housekeeping methods
    def deinit(self):
        try:
            self.time_manager.deinit()
        except:
            pass
        try:
            self.wifi_manager.deinit()
        except:
            pass
        try:
            self.display_manager.deinit()
        except:
            pass
        try:
            self.alarm_manager.deinit()
        except:
            pass
        try:
            self.neopixel_manager.deinit()
        except:
            pass
        try:
            self.button_manager.deinit()
        except:
            pass
        try:
            self.sound_manager.deinit()
        except:
            pass

## Tests

def can_run_sound_alarm_sequence():
    state_mgr = StateManager()
    state_mgr.sound_alarm_sequence()
    sleep(10)
    state_mgr.sound_alarm_stop()

def can_run_sound_alarm_sequence_followed_by_other_operations():
    state_mgr = StateManager()
    state_mgr.sound_alarm_sequence()
    state_mgr.display_compose()