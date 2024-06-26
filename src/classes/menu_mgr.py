class MenuManager:
    def __init__(self, state_mgr):
        self.state = 'idle'  # Possible states: 'idle', 'menu', 'alarm_raised', 'system'
        # 'idle' - normal operation
        # 'menu' - alarm setting mode; was intended to be used for other settings as well, not yet implemented
        # 'alarm_raised' - alarm is ringing
        # 'system' - system information
        self.system_state = 'select' # Possible states: 'select', 'info', 'shutdown'
        # 'select' - select either 'info' or 'shutdown'
        # 'info' - display system information
        # 'shutdown' - power down the system
        self.state_mgr = state_mgr

    def initialize(self):
        self.set_state('idle')
        self.set_system_state('select')

    def set_state(self, state):
        self.state_mgr.log_emit("Setting state to " + state, self.__class__.__name__)
        self.state = state

    def get_state(self):
        return self.state
    
    def set_system_state(self, state):
        self.state_mgr.log_emit("Setting system state to " + state, self.__class__.__name__)
        self.system_state = state

    def get_system_state(self):
        return self.system_state

    def press_green_button(self):
        if self.state == 'idle':
            self.toggle_alarm()
            return
        elif self.state == 'menu':
            self.increase_alarm_hour()
            return
        elif self.state == 'alarm_raised':
            self.attempt_to_quit_alarm('green')
            return
        elif self.state == 'system':
            if self.system_state == 'select':
                self.set_system_state('shutdown')
                return

    def press_blue_button(self):
        if self.state == 'idle':
            self.enter_menu()
            return
        elif self.state == 'menu':
            self.exit_menu()
            return
        elif self.state == 'alarm_raised':
            self.attempt_to_quit_alarm('blue')
            return
        elif self.state == 'system':
            if self.system_state == 'select':
                self.set_system_state('info')
                self.state_mgr.display_compose()

    def press_yellow_button(self):
        if self.state == 'menu':
            self.increase_alarm_minute()
            return
        elif self.state == 'idle':
            self.enter_system()
            return
        elif self.state == 'alarm_raised':
            self.attempt_to_quit_alarm('yellow')
            return
        elif self.state == 'system':
            self.exit_system()
            return

    def toggle_alarm(self):
        self.state_mgr.alarm_set_alarm_active(not self.state_mgr.alarm_is_alarm_active())
        self.state_mgr.display_state_region()
        if self.state_mgr.alarm_is_alarm_active():
            self.state_mgr.neopixel_stop_update_analog_clock_timer()
        else:
            self.state_mgr.neopixel_start_update_analog_clock_timer()

    def enter_menu(self):
        self.set_state('menu')
        self.state_mgr.display_stop_update_display_timer()
        self.state_mgr.alarm_stop_alarm_timer()
        self.state_mgr.display_state_region()
        self.state_mgr.display_time(self.state_mgr.alarm_get_alarm_time())
        self.state_mgr.display_start_blinking_set_alarm_time()

    def exit_menu(self):
        self.set_state('idle')
        self.set_system_state('select')
        self.state_mgr.display_stop_blinking_set_alarm_time()
        self.state_mgr.alarm_write_alarm_time()
        self.state_mgr.alarm_clear_last_alarm_stopped_time()
        self.state_mgr.display_state_region()
        self.state_mgr.display_compose()
        self.state_mgr.display_start_update_display_timer()
        self.state_mgr.alarm_start_alarm_timer()

    def increase_alarm_hour(self):
        time = self.state_mgr.alarm_get_alarm_time()
        hours, minutes = time.split(':')
        hours = (int(hours) + 1) % 24
        time = '{:02d}:{:02d}'.format(hours, int(minutes))
        self.state_mgr.alarm_set_alarm_time(time)

    def increase_alarm_minute(self):
        time = self.state_mgr.alarm_get_alarm_time()
        hours, minutes = time.split(':')
        minutes = (int(minutes) + 1) % 60
        time = '{:02d}:{:02d}'.format(int(hours), minutes)
        self.state_mgr.alarm_set_alarm_time(time)

    def attempt_to_quit_alarm(self, button):
        if len(self.state_mgr.alarm_quit_button_sequence()) > 0:
            if self.state_mgr.alarm_quit_button_sequence()[0] == button:
                self.state_mgr.alarm_remove_first_quit_button_sequence()
                if len(self.state_mgr.alarm_quit_button_sequence()) > 0:
                    self.state_mgr.display_alarm_quit_sequence(0)
                else:
                    self.state_mgr.alarm_quit_alarm()
        else:
            self.state_mgr.alarm_quit_alarm()

    def enter_system(self):
        self.set_state('system')
        self.set_system_state('select')
        self.state_mgr.display_clear()
        self.state_mgr.display_compose()

    def exit_system(self):
        self.set_state('idle')
        self.set_system_state('select')
        self.state_mgr.display_clear()
        self.state_mgr.display_compose()
        
    def deinit(self):
        self.exit_menu()

## Mocks for testing
# use to test the menu manager in isolation

class MockStateManager:
    def __init__(self):
        self.alarm_quit_button_sequence_mocklist = ['green', 'blue', 'yellow']
        self.alarm_active = False
        self.alarm_time = '00:00'
        self.alarm_quit_button_sequence_mocklist = ['green', 'blue', 'yellow']

    def log_emit(self, message, source):
        print(f"{source}: {message}")

    def display_stop_update_display_timer(self):
        pass

    def alarm_stop_alarm_timer(self):
        pass

    def display_state_region(self):
        pass

    def display_time(self, time):
        pass

    def alarm_get_alarm_time(self):
        return self.alarm_time
    
    def alarm_set_alarm_time(self, time):
        self.alarm_time = time
    
    def display_start_blinking_set_alarm_time(self):
        pass

    def display_stop_blinking_set_alarm_time(self):
        pass

    def alarm_clear_last_alarm_stopped_time(self):
        pass

    def display_compose(self):
        pass

    def display_start_update_display_timer(self):
        pass

    def alarm_start_alarm_timer(self):
        pass

    def alarm_set_alarm_active(self, active):
        self.alarm_active = active

    def alarm_is_alarm_active(self):
        return self.alarm_active
    
    def neopixel_stop_update_analog_clock_timer(self):
        pass

    def neopixel_start_update_analog_clock_timer(self):
        pass

    def alarm_write_alarm_time(self):
        pass

    def alarm_quit_button_sequence(self):
        return self.alarm_quit_button_sequence_mocklist
    
    def alarm_remove_first_quit_button_sequence(self):
        self.alarm_quit_button_sequence_mocklist.pop(0)

    def display_alarm_quit_sequence(self, index):
        pass

    def alarm_quit_alarm(self):
        self.alarm_active = False

    def display_clear(self):
        pass

## Tests

def menu_mode_can_be_entered_and_exited():
    #[GIVEN]: A menu manager
    state_mgr = MockStateManager()
    menu_mgr = MenuManager(state_mgr)
    #[WHEN]: The menu mode is entered
    menu_mgr.enter_menu()
    #[THEN]: The state is 'menu'
    assert menu_mgr.state == 'menu', "State is not 'menu'"
    #[WHEN]: The menu mode is exited
    menu_mgr.exit_menu()
    #[THEN]: The state is 'idle'
    assert menu_mgr.state == 'idle', "State is not 'idle'"
    #[TEARDOWN]:
    menu_mgr.deinit()

def alarm_can_be_toggled():
    #[GIVEN]: A menu manager
    state_mgr = MockStateManager()
    menu_mgr = MenuManager(state_mgr)
    #[WHEN]: The alarm is toggled
    menu_mgr.toggle_alarm()
    #[THEN]: The alarm is active
    assert state_mgr.alarm_active == True, "Alarm is not active"
    #[WHEN]: The alarm is toggled again
    menu_mgr.toggle_alarm()
    #[THEN]: The alarm is not active
    assert state_mgr.alarm_active == False, "Alarm is active"
    #[TEARDOWN]:
    menu_mgr.deinit()

def alarm_time_can_be_altered():
    #[GIVEN]: A menu manager
    state_mgr = MockStateManager()
    menu_mgr = MenuManager(state_mgr)
    #[GIVEN]: The alarm time is '11:11'
    state_mgr.alarm_time = '11:11'
    #[WHEN]: The alarm time is increased
    menu_mgr.enter_menu()
    menu_mgr.increase_alarm_hour()
    #[THEN]: The alarm time is increased
    assert state_mgr.alarm_time == '12:11', "Alarm time is not '12:11'"
    #[WHEN]: The alarm time is increased again
    menu_mgr.increase_alarm_minute()
    #[THEN]: The alarm time is increased
    assert state_mgr.alarm_time == '12:12', "Alarm time is not '12:12'"
    #[TEARDOWN]:
    menu_mgr.deinit()

def alarm_quit_sequence_can_be_interrupted():
    #[GIVEN]: A menu manager
    state_mgr = MockStateManager()
    menu_mgr = MenuManager(state_mgr)
    #[WHEN]: The correct sequence is entered
    menu_mgr.attempt_to_quit_alarm('green')
    menu_mgr.attempt_to_quit_alarm('blue')
    menu_mgr.attempt_to_quit_alarm('yellow')
    #[THEN]: The alarm is quit
    assert state_mgr.alarm_active == False, "Alarm is still active"
    #[TEARDOWN]:
    menu_mgr.deinit()

def system_can_be_entered_and_exited():
    #[GIVEN]: A menu manager
    state_mgr = MockStateManager()
    menu_mgr = MenuManager(state_mgr)
    #[WHEN]: The system info is entered
    menu_mgr.enter_system()
    #[THEN]: The state is 'system'
    assert menu_mgr.state == 'system', "State is not 'system'"
    #[WHEN]: The system info is exited
    menu_mgr.exit_system()
    #[THEN]: The state is 'idle'
    assert menu_mgr.state == 'idle', "State is not 'idle'"
    #[TEARDOWN]:
    menu_mgr.deinit()

def pressing_yellow_button_enters_and_exits_system():
    #[GIVEN]: A menu manager
    state_mgr = MockStateManager()
    menu_mgr = MenuManager(state_mgr)
    #[WHEN]: The yellow button is pressed
    menu_mgr.press_yellow_button()
    #[THEN]: The state is 'system'
    assert menu_mgr.state == 'system', "State is not 'system'"
    #[WHEN]: The yellow button is pressed again
    menu_mgr.press_yellow_button()
    #[THEN]: The state is 'idle'
    assert menu_mgr.state == 'idle', "State is not 'idle'"
    #[TEARDOWN]:
    menu_mgr.deinit()