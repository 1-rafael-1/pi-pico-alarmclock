from drivers.dfplayer_mini import DFPlayerMini
from utime import sleep

class SoundManager:
    def __init__(self, state_mgr):
        self.player = DFPlayerMini(uartinstance=0, tx_pin=0, rx_pin=1, power_pin=8)
        self.state_mgr = state_mgr

    def delay(self):
        self.state_mgr.log_emit("Delaying", self.__class__.__name__)
        self.player.begin()

    def reset(self):
        self.state_mgr.log_emit("Resetting player", self.__class__.__name__)
        self.player.reset()

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
        self.power_on()
        self.state_mgr.log_emit("Powering on", self.__class__.__name__)
        for i in range(1, 20):
            self.delay()
            i += 1
        self.state_mgr.log_emit("Should be powered on", self.__class__.__name__)
        self.set_eq(4) # classic
        self.delay()
        self.set_volume(10) # medium volume
        self.delay()
        self.play(1)
        self.delay()

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