from drivers.dfplayer_mini import DFPlayerMini
from utime import sleep

class SoundManager:
    def __init__(self, state_mgr):
        self.player = DFPlayerMini(uartinstance=0, tx_pin=0, rx_pin=1, power_pin=8)
        self.state_mgr = state_mgr

    def delay(self):
        self.player.begin()

    def reset(self):
        self.player.reset()

    def set_eq(self, eq):
        self.player.set_equalizer(eq)

    def set_volume(self, volume):
        self.player.set_volume(volume)

    def play(self, track):
        self.player.play_track(track)

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.resume()

    def stop(self):
        self.player.stop()

    def standby(self):
        self.player.sleep()

    def wake_up(self):
        self.player.wake_up()

    def power_on(self):
        self.player.power_on()

    def power_off(self):
        self.player.power_off()

    def alarm_sequence(self):
        print("Playing alarm sequence")
        self.power_on()
        for i in range(1, 6):
            self.delay()
            i += 1
        self.set_eq(4) # classic
        self.delay()
        self.set_volume(10) # medium volume
        self.delay()
        self.play(1)
        self.delay()

    def alarm_stop(self):
        print("Stopping alarm sequence")
        self.power_off()

    def deinit(self):
        self.delay()
        self.standby()

## Mocks for testing
# use to test SoundManager in isolation

class MockStateManager:
    def __init__(self):
        self.alarm_time = "00:00"
        self.alarm_active = False
        self.alarm_raised = False
    
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