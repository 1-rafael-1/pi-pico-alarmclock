import micropython
from utime import sleep, time, gmtime, ticks_ms, ticks_diff
from random import randint
from machine import Pin, Timer
import neopixel

class NeoPixelManager:
    def __init__(self, state_mgr, ledCount=16, ctrlPin=28):
        self.np = neopixel.NeoPixel(pin=Pin(ctrlPin), n=ledCount)
        self.state_mgr = state_mgr
        self.update_analog_clock_timer = None
        
    def initialize(self):
        self.all_off()

    def start_update_analog_clock_timer(self):
        if self.update_analog_clock_timer is None:
           self.state_mgr.log_emit("Starting update analog clock timer", self.__class__.__name__)
           self.all_off()
           self.analog_clock(brightness=0.01)
           self.update_analog_clock_timer = Timer(period=3750, mode=Timer.PERIODIC, callback=lambda t: self.analog_clock(brightness=0.01))

    def stop_update_analog_clock_timer(self):
        self.state_mgr.log_emit("Stopping update analog clock timer", self.__class__.__name__)
        if self.update_analog_clock_timer is not None:
            self.state_mgr.log_emit("Stopping update analog clock timer", self.__class__.__name__)
            self.update_analog_clock_timer.deinit()
            self.update_analog_clock_timer = None
            self.all_off()

    @micropython.native
    def all_off(self):
        self.np.fill((0, 0, 0))
        self.np.write()
        sleep(.1) # neopixel needs some time to turn off

    @micropython.native
    def get_color(self, red=0, green=0, blue=0, brightness=0.2):
        return (int(red * brightness), int(green * brightness), int(blue * brightness))

    @micropython.native
    def all_on(self, color):
        self.np.fill(color)
        self.np.write()

    @micropython.native
    def single_on(self, color, ledIndex):
        self.np[ledIndex] = color
        self.np.write()

    def get_now(self):
        return gmtime(time())

    @micropython.native
    def pendulum(self, colors, delay=0.1, loops=3):
        while loops > 0:
            if not self.state_mgr.alarm_is_alarm_raised():
                break
            for i in range(self.np.n):
                for j, color in enumerate(colors):
                    self.np[(i+j)%self.np.n] = color
                self.np.write()
                sleep(delay)
                for j in range(len(colors)):
                    self.np[(i+j)%self.np.n] = (0, 0, 0)
            for i in range(self.np.n-1, -1, -1):
                for j, color in enumerate(colors):
                    self.np[(i+j)%self.np.n] = color
                self.np.write()
                sleep(delay)
                for j in range(len(colors)):
                    self.np[(i+j)%self.np.n] = (0, 0, 0)
            loops -= 1

    @micropython.native
    def chase(self, colors, delay=0.1, loops=3):
        while loops > 0:
            if not self.state_mgr.alarm_is_alarm_raised():
                break
            for i in range(self.np.n):
                for j, color in enumerate(colors):
                    self.np[(i+j)%self.np.n] = color
                self.np.write()
                sleep(delay)
                self.np[i] = (0, 0, 0)
            loops -= 1

    @micropython.native
    def turning_wheel(self, color, delay=0.1, loops=3):
        for i in range(self.np.n):
            if i % 2 == 0:
                self.np[i] = color
            else:
                self.np[i] = (0, 0, 0)
        self.np.write()
        sleep(delay)
        for _ in range(loops):
            if not self.state_mgr.alarm_is_alarm_raised():
                break
            for i in range(self.np.n):
                if i % 2 == 0:
                    self.np[i] = (0, 0, 0)
                else:
                    self.np[i] = color
            self.np.write()
            sleep(delay)
            for i in range(self.np.n):
                if i % 2 == 0:
                    self.np[i] = color
                else:
                    self.np[i] = (0, 0, 0)
            self.np.write()
            sleep(delay)

    @micropython.native
    def analog_clock(self, brightness=0.05):
        hour_color = self.get_color(255, 0, 0, brightness)  # Red
        minute_color = self.get_color(0, 255, 0, brightness)  # Green
        second_color = self.get_color(0, 0, 255, brightness)  # Blue
        
        # Get the current time
        loc_time = self.get_now()
        hour = (loc_time[3] % 12) or 12
        minute = loc_time[4]
        second = loc_time[5]

        # Calculate the LED indices for each hand
        # the hour hand will deliberately be dragging behind since we choose to not account for minutes passed in the hour
        hour_index = int(hour / 12 * self.np.n) - int(self.np.n / 2)
        minute_index = int(minute / 60 * self.np.n) - int(self.np.n / 2)
        second_index = int(second / 60 * self.np.n) - int(self.np.n / 2)
        
        self.np.fill((0, 0, 0))
        
        # if hourIndex, minuteIndex, secondIndex are the same in some combo, the color will be mixed
        # this is a stupid way to do it, but it works
        if hour_index == minute_index == second_index:
            # all hands are on the same LED
            mix_color = (int((hour_color[0] + minute_color[0] + second_color[0]) / 3), int((hour_color[1] + minute_color[1] + second_color[1]) / 3), int((hour_color[2] + minute_color[2] + second_color[2]) / 3))
            self.single_on(mix_color, hour_index)
        elif hour_index == minute_index:
            # hour and minute hands are on the same LED
            mix_color = (int((hour_color[0] + minute_color[0]) / 2), int((hour_color[1] + minute_color[1]) / 2), int((hour_color[2] + minute_color[2]) / 2))
            self.single_on(mix_color, hour_index)
            self.single_on(second_color, second_index)
        elif hour_index == second_index:
            # hour and second hands are on the same LED
            mix_color = (int((hour_color[0] + second_color[0]) / 2), int((hour_color[1] + second_color[1]) / 2), int((hour_color[2] + second_color[2]) / 2))
            self.single_on(mix_color, hour_index)
            self.single_on(minute_color, minute_index)
        elif minute_index == second_index:
            # minute and second hands are on the same LED
            mix_color = (int((minute_color[0] + second_color[0]) / 2), int((minute_color[1] + second_color[1]) / 2), int((minute_color[2] + second_color[2]) / 2))
            self.single_on(mix_color, minute_index)
            self.single_on(hour_color, hour_index)
        else:    
            # no hands are on the same LED
            self.single_on(hour_color, hour_index)
            self.single_on(minute_color, minute_index)
            self.single_on(second_color, second_index)
        
        self.np.write()

    @micropython.native
    def sunrise(self, duration=None):
        start_color = self.get_color(255, 0, 0)  # Red
        end_color = self.get_color(255, 221, 148)  # Warm white
        start_brightness = 0.1  # Very low brightness
        end_brightness = 1.0  # Full brightness
        if duration is None:
            duration = 300  # 5 minutes
        start_time = ticks_ms()

        while True:
            if not self.state_mgr.alarm_is_alarm_raised():
                break
            elapsed_time = ticks_diff(ticks_ms(), start_time) / 1000  # Convert to seconds
            if elapsed_time > duration:
                break        

            # Calculate the current brightness and color based on the elapsed time
            t = elapsed_time / duration  # t goes from 0 to 1 over the duration
            current_brightness = start_brightness + t * (end_brightness - start_brightness)
            current_color = (
                int(start_color[0] + t * (end_color[0] - start_color[0])),
                int(start_color[1] + t * (end_color[1] - start_color[1])),
                int(start_color[2] + t * (end_color[2] - start_color[2])),
            )

            # Calculate the number of LEDs to light up based on the elapsed time
            num_leds = int(self.np.n * t) + 1
            for i in range(num_leds):
                self.np[i] = current_color
            self.np.write()

            sleep(1)  # Update every second

    def deinit(self):
        self.stop_update_analog_clock_timer()
        self.all_off()


## Mocks for testing
# use to test NeoPixelManager in isolation

class MockStateManager:
    def __init__(self):
        self.alarm_time = "00:00"
        self.alarm_active = False
        self.alarm_raised = False

    def alarm_is_alarm_raised(self):
        return self.alarm_raised
    
## Tests

def single_on_switches_single_led_on():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[WHEN]: NeoPixelManager lights up a single LED
    np_mgr.single_on((0, 255, 0), 0)
    #[THEN]: NeoPixelManager has a single LED lit
    sleep(1)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()

def all_on_switches_all_leds_on():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[WHEN]: NeoPixelManager lights up all LEDs
    np_mgr.all_on((0, 0, 255))
    #[THEN]: NeoPixelManager has all LEDs lit
    sleep(1)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()

def pendulum_runs_pendulum_effect():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[GIVEN]: we are in alarm raised state
    state_mgr.alarm_raised = True
    #[WHEN]: NeoPixelManager runs a pendulum effect
    np_mgr.pendulum([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    #[THEN]: NeoPixelManager has a pendulum effect running
    sleep(1)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()

def chase_runs_chase_effect():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[GIVEN]: we are in alarm raised state
    state_mgr.alarm_raised = True
    #[WHEN]: NeoPixelManager runs a chase effect
    np_mgr.chase([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    #[THEN]: NeoPixelManager has a chase effect running
    sleep(1)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()

def turning_wheel_runs_turning_wheel_effect():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[GIVEN]: we are in alarm raised state
    state_mgr.alarm_raised = True
    #[WHEN]: NeoPixelManager runs a turning wheel effect
    np_mgr.turning_wheel((255, 0, 0))
    #[THEN]: NeoPixelManager has a turning wheel effect running
    sleep(1)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()

def analog_clock_runs_analog_clock_effect():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[WHEN]: NeoPixelManager runs an analog clock effect
    np_mgr.analog_clock()
    #[THEN]: NeoPixelManager has an analog clock effect running
    #[THEN]: we can compare the current time with the LED colors
    print("Current time: ", np_mgr.get_now())
    sleep(3)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()

def analog_clock_runs_analog_clock_effect_on_timer():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[WHEN]: NeoPixelManager starts an analog clock effect timer
    np_mgr.start_update_analog_clock_timer()
    #[THEN]: NeoPixelManager has an analog clock effect running on a timer
    sleep(20)
    #[TEARDOWN]: NeoPixelManager stops the analog clock effect timer
    np_mgr.stop_update_analog_clock_timer()

def sunrise_runs_sunrise_effect():
    #[GIVEN]: NeoPixelManager instance
    state_mgr = MockStateManager()
    np_mgr = NeoPixelManager(state_mgr)
    #[GIVEN]: we are in alarm raised state
    state_mgr.alarm_raised = True
    #[WHEN]: NeoPixelManager runs a sunrise effect
    np_mgr.sunrise(duration=15)
    #[THEN]: NeoPixelManager has a sunrise effect running
    sleep(1)
    #[TEARDOWN]: NeoPixelManager turns off all LEDs
    np_mgr.all_off()