import _thread
from utime import sleep
from machine import freq
from classes.log_mgr import LogManager
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
        self.log_manager = LogManager(self)
        self.power_manager = PowerManager(self)
        self.wifi_manager = WifiManager(self)
        self.time_manager = TimeManager(self)
        self.neopixel_manager = NeoPixelManager(self)
        self.display_manager = DisplayManager(self)
        self.menu_manager = MenuManager(self)
        self.button_manager = ButtonManager(self, green_pin=20, blue_pin=21, yellow_pin=22)
        self.sound_manager = SoundManager(self)
        self.alarm_manager = AlarmManager(self)
        self.lowpower_manager = LowPowerManager(self, green_pin=self.button_manager.get_green_pin(), blue_pin=self.button_manager.get_blue_pin() , yellow_pin=self.button_manager.get_yellow_pin())
        self.lock = _thread.allocate_lock()

    def initialize(self):
        self.log_initialize()
        self.log_emit("Initializing StateManager", self.__class__.__name__)

        self.set_full_clock_speed()

        self.display_initialize()
        self.display_compose_boot('display mgr')

        self.menu_initialize()

        self.display_compose_boot('power mgr')
        self.power_initialize()

        self.display_compose_boot('wifi + rtc')
        self.time_initialize()
        self.time_start_update_rtc_timer()

        self.display_compose_boot('alarm mgr')
        self.alarm_initialize()
        self.alarm_start_alarm_timer()

        self.display_compose_boot('neopixel')
        self.neopixel_initialize()
        if not self.alarm_is_alarm_active():
            self.neopixel_start_update_analog_clock_timer()

        self.display_compose_boot('button mgr') 
        self.button_initialize()
        
        self.display_compose_boot('normal op')
        self.display_initialize_normal_operation()
        self.display_start_update_display_timer()

        self.log_emit("StateManager initialized", self.__class__.__name__)

    # region global state methods
    def set_full_clock_speed(self):
        freq(125000000) # 125 MHz, default clock speed for RP2040
        sleep(1) # wait for clock speed to stabilize
        self.log_emit(f"Clock speed set to: {freq()}", self.__class__.__name__)

    def set_low_clock_speed(self):
        freq(20000000) # 20 MHz, lowest clock speed for RP2040
        sleep(1) # wait for clock speed to stabilize
        self.log_emit(f"Clock speed set to: {freq()}", self.__class__.__name__)
    # endregion

    # region PowerManager methods
    def power_initialize(self):
        self.power_manager.initialize()

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
    
    def power_log_vsys(self):
        self.power_manager.log_vsys()
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
    def menu_initialize(self):
        self.menu_manager.initialize()

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
    
    def menu_set_system_state(self, state):
        self.menu_manager.set_system_state(state)
    
    def menu_get_system_state(self):
        return self.menu_manager.get_system_state()
    
    def menu_is_menu_active(self):
        return self.menu_manager.get_state() in ['system','menu']
    # endregion

    # region DisplayManager methods
    def display_initialize(self):
        self.display_manager.initialize()

    def display_clear(self):
        self.display_manager.clear()

    def display_compose(self):
        self.display_manager.compose()

    def display_compose_boot(self, message):
        self.display_manager.compose_boot(message)

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

    def display_initialize_normal_operation(self):
        self.display_manager.initialize_normal_operation()
    # endregion

    # region NeoPixelManager methods
    def neopixel_initialize(self):
        self.neopixel_manager.initialize()

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
    def alarm_initialize(self):
        self.alarm_manager.initialize()

    def alarm_start_alarm_timer(self):
        self.alarm_manager.start_alarm_timer()

    def alarm_stop_alarm_timer(self):
        self.alarm_manager.stop_alarm_timer()

    def alarm_set_alarm_raised(self, value):
        self.alarm_manager.set_alarm_raised = value

    def alarm_is_alarm_raised(self):
        with self.lock:
            return self.alarm_manager.is_alarm_raised()

    def alarm_set_alarm_active(self, value):
        self.alarm_manager.set_alarm_active(value)

    def alarm_is_alarm_active(self):
        return self.alarm_manager.is_alarm_active()
    
    def alarm_set_alarm_time(self, value):
        self.alarm_manager.set_alarm_time(value)

    def alarm_get_alarm_time(self):
        return self.alarm_manager.get_alarm_time()
    
    def alarm_write_alarm_time(self):
        self.alarm_manager.write_alarm_time()

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

    # region LogManager methods
    def log_initialize(self):
        self.log_manager.initialize()

    def log_emit(self, message, source_class):
        self.log_manager.emit(message, source_class)

    def log_set_verbose(self, value):
        self.log_manager.set_verbose(value)

    def log_set_log(self, value):
        self.log_manager.set_log(value)

    def log_get_verbose(self):
        return self.log_manager.get_verbose()
    
    def log_get_log(self):
        return self.log_manager.get_log()
    
    def log_set_max_log_length(self, value):
        self.log_manager.set_max_log_length(value)

    def log_get_max_log_length(self):
        return self.log_manager.get_max_log_length()
    
    def log_set_log_file(self, value):
        self.log_manager.set_log_file(value)

    def log_get_log_file(self):
        return self.log_manager.get_log_file()
    
    def log_set_clean_log(self, value):
        self.log_manager.set_clean_log(value)

    def log_get_clean_log(self):
        return self.log_manager.get_clean_log()
    # endregion

    # region TimeManager methods
    def time_initialize(self):
        self.time_manager.initialize()

    def time_start_update_rtc_timer(self):
        self.time_manager.start_update_rtc_timer()
    # endregion

    # region ButtonManager methods
    def button_initialize(self):
        self.button_manager.initialize()
    # endregion

    # region housekeeping methods
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
        try:
            self.log_manager.deinit()
        except:
            pass
    # endregion

## Tests

def can_initialize_state_manager():
    state_mgr = StateManager()
    state_mgr.initialize()
    sleep(5)
    state_mgr.deinit()

def can_run_sound_alarm_sequence():
    state_mgr = StateManager()
    state_mgr.sound_alarm_sequence()
    sleep(10)
    state_mgr.sound_alarm_stop()
    sleep(5)
    state_mgr.deinit()

def can_run_sound_alarm_sequence_followed_by_other_operations():
    state_mgr = StateManager()
    state_mgr.sound_alarm_sequence()
    state_mgr.display_compose()

def can_run_alarm_sequence_when_all_other_devices_are_initialized():
    state_mgr = StateManager()
    state_mgr.initialize()
    state_mgr.sound_alarm_sequence()
    sleep(5)
    state_mgr.sound_alarm_stop()
    state_mgr.deinit()
