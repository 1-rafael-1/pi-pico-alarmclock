import micropython
from utime import sleep, time, localtime
from machine import Timer
from urandom import randint
import _thread

class AlarmManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        self.alarm_timer = None
        self.alarm_raised_time = None
        self.last_alarm_stopped_time = None
        self.alarm_quit_button_sequence = []
        self.alarm_sequence_thread = None
        self.alarm_sequence_running = False
        self.alarm_sequence_sound_running = False

    def start_alarm_timer(self):
        if self.alarm_timer is None:
            self.alarm_timer = Timer(period=30000, mode=Timer.PERIODIC,callback=lambda t: self.check_alarm())
        
    def stop_alarm_timer(self):
        if self.alarm_timer is not None:
            self.alarm_timer.deinit()
            self.alarm_timer = None
        self.state_mgr.alarm_set_alarm_raised(False)

    def set_last_alarm_stopped_time(self, time):
        self.last_alarm_stopped_time = time

    def clear_last_alarm_stopped_time(self):
        self.last_alarm_stopped_time = None

    def is_last_alarm_just_stopped(self):
        if self.last_alarm_stopped_time is not None:
            if time() - self.last_alarm_stopped_time <= 600:
                return True
        return False

    @micropython.native
    def check_alarm(self):
        if self.state_mgr.is_alarm_active() and not self.state_mgr.alarm_is_alarm_raised() and not self.is_last_alarm_just_stopped():
            current_time = localtime()
            current_hours = current_time[3]
            current_minutes = current_time[4]
            alarm_hours, alarm_minutes = map(int, self.state_mgr.alarm_time.split(':'))
            print(f'Alarm time: {self.state_mgr.alarm_time} Current time: {current_hours}:{current_minutes}')
        
            # Calculate the difference in minutes between the current time and the alarm time
            time_diff = (current_hours * 60 + current_minutes) - (alarm_hours * 60 + alarm_minutes)
            
            # Adjust the time difference for the case where the current time is on the next day
            if time_diff < -30:  # The current time is on the next day
                time_diff += 24 * 60  # Add 24 hours to the time difference
        
            if -5 <= time_diff <= 3:
                if not self.state_mgr.alarm_is_alarm_raised():
                    self.raise_alarm()
        elif self.state_mgr.alarm_is_alarm_raised():
            if self.alarm_raised_time is not None:
                print(f"elapsed seconds since alarm raised: {time() - self.alarm_raised_time}")
            if self.alarm_raised_time is not None:
                if time() - self.alarm_raised_time >= 300:  # 5 minutes
                    if not self.alarm_sequence_sound_running:
                        self.alarm_sequence_sound_running = True
                        self.state_mgr.sound_alarm_sequence()
                if time() - self.alarm_raised_time >= 600:  # 10 minutes
                    self.quit_alarm()
                    self.alarm_raised_time = None

    @micropython.native
    def randomize_quit_button_sequenze(self):
        colors = ['green', 'blue', 'yellow']
        self.alarm_quit_button_sequence = []
        while colors:
            index = randint(0, len(colors) - 1)
            self.alarm_quit_button_sequence.append(colors.pop(index))

    def display_first_quit_button_sequence(self):
        self.state_mgr.display_alarm_quit_sequence(0)

    def remove_first_quit_button_sequence(self):
        self.alarm_quit_button_sequence.pop(0)

    @micropython.native
    def alarm_sequence(self):
        self.set_alarm_sequence_running(True)
        self.state_mgr.neopixel_all_off()
        self.state_mgr.neopixel_sunrise(duration=300)
        # self.state_mgr.sound_alarm_sequence() # async, non-blocking
        # sleep(5) # wait for sound to start
        while self.state_mgr.alarm_is_alarm_raised():
            for i in range(7):
                if not self.state_mgr.alarm_is_alarm_raised():
                    break
                if i == 0: 
                    self.state_mgr.neopixel_all_off()
                elif i == 1: 
                    self.state_mgr.neopixel_turning_wheel(self.state_mgr.neopixel_get_color(255, 255, 255), delay=0.3, loops=10)
                elif i == 2: 
                    self.state_mgr.neopixel_all_off()
                elif i == 3: 
                    self.state_mgr.neopixel_chase([self.state_mgr.neopixel_get_color(255, 0, 0), self.state_mgr.neopixel_get_color(0, 255, 0), self.state_mgr.neopixel_get_color(0, 0, 255), self.state_mgr.neopixel_get_color(255, 255, 0), self.state_mgr.neopixel_get_color(0, 255, 255)], delay=0.1, loops=5)
                elif i == 4: 
                    self.state_mgr.neopixel_all_off()
                elif i == 5: 
                    self.state_mgr.neopixel_pendulum([self.state_mgr.neopixel_get_color(255, 0, 0), self.state_mgr.neopixel_get_color(0, 255, 0), self.state_mgr.neopixel_get_color(0, 0, 255)], delay=0.1, loops=5)
                elif i == 6: 
                    self.state_mgr.neopixel_all_off() 
        self.state_mgr.neopixel_all_off()
        self.set_alarm_sequence_running(False)

    def start_alarm_sequence_thread(self):
        _thread.stack_size(6*1024) # the default stack size (4kb) is too small once the thread is started. Max. recursion depth exceptions will occur anywhere.  
        self.alarm_sequence_thread = _thread.start_new_thread(lambda: self.alarm_sequence(), ())
    
    def set_alarm_sequence_running(self, value):
        self.alarm_sequence_running = value

    def is_alarm_sequence_running(self):
        return self.alarm_sequence_running

    @micropython.native
    def raise_alarm(self):
        self.state_mgr.set_full_clock_speed()
        self.clear_last_alarm_stopped_time()
        self.randomize_quit_button_sequenze()
        self.state_mgr.alarm_set_alarm_raised(True)
        self.state_mgr.menu_set_state('alarm_raised')
        self.alarm_raised_time = time()
        self.state_mgr.neopixel_stop_update_analog_clock_timer()
        self.state_mgr.neopixel_all_off()
        sleep(.1) # neopixel needs some time to turn off
        self.start_alarm_sequence_thread()
        self.display_first_quit_button_sequence()
        
    @micropython.native
    def quit_alarm(self):
        self.set_last_alarm_stopped_time(time())
        self.state_mgr.alarm_set_alarm_raised(False)
        self.alarm_raised_time = None
        self.state_mgr.neopixel_all_off()
        self.state_mgr.sound_alarm_stop()
        self.alarm_sequence_sound_running = False
        self.state_mgr.neopixel_start_update_analog_clock_timer()
        self.state_mgr.display_clear_first_row()
        self.state_mgr.menu_set_state('idle')
        self.state_mgr.display_compose()
        self.state_mgr.set_medium_clock_speed()
        
    def deinit(self):
        self.stop_alarm_timer()
        self.quit_alarm()


## Mocks for testing
# use to test AlarmManager in isolation

class MockStateManager:
    def __init__(self):
        self.alarm_time = "00:00"
        self.alarm_active = False
        self.alarm_raised = False

    def is_alarm_active(self):
        return self.alarm_active

    def alarm_is_alarm_raised(self):
        return self.alarm_raised
    
    def alarm_set_alarm_raised(self, value):
        self.alarm_raised = value

    def get_alarm_time(self):
        return self.alarm_time

    def set_alarm_time(self, time):
        self.alarm_time = time

    def neopixel_stop_update_analog_clock_timer(self):
        print("Neopixel stop update analog clock timer")

    def start_alarm_sequence_thread(self):
        print("Neopixel start alarm sequence thread")
    
    def neopixel_start_update_analog_clock_timer(self):
        print("Neopixel start update analog clock timer")

    def menu_set_state(self, state):
        print(f"Menu set state: {state}")

    def display_alarm_quit_sequence(self, index):
        print(f"Display alarm quit sequence: {index}")

    def display_clear_first_row(self):
        print("Display clear first row")

    def display_compose(self):
        print("Display compose")

    def sound_alarm_sequence(self):
        print("Sound alarm sequence")

    def sound_alarm_stop(self):
        print("Sound alarm stop")

    def neopixel_all_off(self):
        print("Neopixel all off")

    def neopixel_sunrise(self, duration):
        print(f"Neopixel sunrise: {duration}")

    def neopixel_pendulum(self, colors, delay, loops):
        print(f"Neopixel pendulum: {colors}, {delay}, {loops}")

    def neopixel_chase(self, colors, delay, loops):
        print(f"Neopixel chase: {colors}, {delay}, {loops}")
    
    def neopixel_turning_wheel(self, color, delay, loops):
        print(f"Neopixel turning wheel: {color}, {delay}, {loops}")

    def neopixel_get_color(self, r, g, b):
        return (r, g, b)
    


## Tests

def alarm_manager_runs():
    #[GIVEN]: AlarmManager instance
    print("Test AlarmManager")
    state_mgr = MockStateManager()
    alarm_mgr = AlarmManager(state_mgr)
    #[WHEN]: AlarmManager Timer is started
    alarm_mgr.start_alarm_timer()
    #[THEN]: AlarmManager Timer is running
    sleep(10)
    #[WHEN]: AlarmManager Timer gets stopped
    alarm_mgr.stop_alarm_timer()
    #[THEN]: AlarmManager Timer is stopped

def alarm_manager_raises_alarm():
    #[GIVEN]: AlarmManager instance
    print("Test AlarmManager raise alarm")
    state_mgr = MockStateManager()
    alarm_mgr = AlarmManager(state_mgr)
    #[WHEN]: AlarmManager raises alarm
    alarm_mgr.raise_alarm()
    #[THEN]: AlarmManager alarm is raised
    sleep(10)
    #[WHEN]: AlarmManager quits alarm
    alarm_mgr.quit_alarm()
    #[THEN]: AlarmManager alarm is quit

def alarm_manager_randomizes_quit_button_sequence():
    #[GIVEN]: AlarmManager instance
    print("Test AlarmManager randomize quit button sequence")
    state_mgr = MockStateManager()
    alarm_mgr = AlarmManager(state_mgr)
    #[WHEN]: AlarmManager randomizes quit button sequence
    alarm_mgr.randomize_quit_button_sequenze()
    #[THEN]: AlarmManager quit button sequence is randomized
    print(alarm_mgr.alarm_quit_button_sequence)