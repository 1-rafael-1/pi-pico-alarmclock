from drivers.dfplayer_mini import DFPlayerMini
from utime import sleep

class SoundManager:
    def __init__(self, state_mgr):
        self.player = DFPlayerMini(uartinstance=1, tx_pin=4, rx_pin=5, power_pin=8, busy_pin=3)
        self.state_mgr = state_mgr

    def delay(self, times=1):
        for i in range(1, times):
            self.state_mgr.log_emit("Delaying", self.__class__.__name__)
            self.player.begin()
            i += 1

    def reset(self):
        self.state_mgr.log_emit("Resetting player", self.__class__.__name__)
        self.player.reset()

    def is_busy(self):
        return self.player.is_busy()

    def set_eq(self, eq):
        self.state_mgr.log_emit("Setting equalizer to " + str(eq), self.__class__.__name__)
        self.player.set_equalizer(eq)

    def set_volume(self, volume):
        self.state_mgr.log_emit("Setting volume to " + str(volume), self.__class__.__name__)
        self.player.set_volume(volume)

    def play(self, track):
        self.state_mgr.log_emit("Playing track " + str(track), self.__class__.__name__)
        self.player.play_track(track)

    def pause(self):
        self.state_mgr.log_emit("Pausing", self.__class__.__name__)
        self.player.pause()

    def resume(self):
        self.state_mgr.log_emit("Resuming", self.__class__.__name__)
        self.player.resume()

    def stop(self):
        self.state_mgr.log_emit("Stopping", self.__class__.__name__)
        self.player.stop()

    def standby(self):
        self.state_mgr.log_emit("Standing by", self.__class__.__name__)
        self.player.sleep()

    def wake_up(self):
        self.state_mgr.log_emit("Waking up", self.__class__.__name__)
        self.player.wake_up()

    def power_on(self):
        self.state_mgr.log_emit("Powering on", self.__class__.__name__)
        self.player.power_on()

    def power_off(self):
        self.state_mgr.log_emit("Powering off", self.__class__.__name__)
        self.player.power_off()

    def alarm_sequence(self):
        self.state_mgr.log_emit("Playing alarm sequence", self.__class__.__name__)
        self.state_mgr.log_emit("Powering on", self.__class__.__name__)
        self.power_on()
        self.delay(5)
        self.state_mgr.log_emit("Should be powered on", self.__class__.__name__)
        self.set_eq(4) # classic
        self.delay(2)
        self.set_volume(5) # medium volume
        self.delay(3)
        max_tries = 20
        i = 0
        self.play(1)
        self.delay(3)
        while self.is_busy() == False:
            self.state_mgr.log_emit("Repeated attempt to wait for busy", self.__class__.__name__)
            self.delay(1)
            i += 1
            if i >= max_tries:
                self.state_mgr.log_emit("Failed to wait for busy", self.__class__.__name__)
                break
        i = 0
        while self.is_busy() == False:
            self.state_mgr.log_emit("Repeated attempt to play alarm sound", self.__class__.__name__)
            self.play(1)  
            self.delay(5)
            i += 1
            if i >= max_tries:
                self.state_mgr.log_emit("Failed to play alarm sound", self.__class__.__name__)
                break
        self.delay(1)

    def alarm_stop(self):
        self.state_mgr.log_emit("Stopping alarm sequence", self.__class__.__name__)
        self.power_off()

    def deinit(self):
        self.delay()
        self.power_off()

## Mocks for testing
# use to test SoundManager in isolation

class MockStateManager:
    def __init__(self):
        self.alarm_time = "00:00"
        self.alarm_active = False
        self.alarm_raised = False

    def log_emit(self, msg, source):
        print(f"{source}: {msg}")
    
## Tests
def sound_manager_alarm_sequence_can_start_and_stop():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager alarm sequence")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager starts the alarm sequence
    sound_mgr.alarm_sequence()
    #[THEN]: SoundManager is playing the alarm sequence
    sleep(10)
    #[WHEN]: SoundManager stops the alarm sequence
    sound_mgr.alarm_stop()
    #[THEN]: SoundManager is stopped