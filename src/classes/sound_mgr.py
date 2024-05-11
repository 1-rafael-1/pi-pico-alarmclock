from drivers.dfplayer_mini import DFPlayerMini
from utime import sleep

class SoundManager:
    def __init__(self, state_mgr):
        self.player = DFPlayerMini(uartinstance=0, tx_pin=0, rx_pin=1, power_pin=16)
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
        self.delay()
        self.wake_up()
        self.delay()
        self.reset()
        self.delay()
        self.set_eq(4) # classic
        self.delay()
        self.set_volume(10) # medium volume
        self.delay()
        self.play(1) 
        self.delay()

    def alarm_stop(self):
        print("Stopping alarm sequence")
        self.delay()
        self.stop()
        self.delay()
        self.standby()

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
def sound_manager_runs():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    sound_mgr.delay()
    sound_mgr.set_volume(5)
    #[WHEN]: SoundManager plays a track
    print("Playing track 1")
    sound_mgr.delay()
    sound_mgr.play(1)
    #[THEN]: SoundManager is playing the track
    sleep(10)
    print("pause")
    #[WHEN]: SoundManager pauses the track
    sound_mgr.delay()
    sound_mgr.pause()
    #[THEN]: SoundManager is paused
    sleep(10)
    #[WHEN]: SoundManager resumes the track
    print("resume")
    sound_mgr.delay()
    sound_mgr.resume()
    #[THEN]: SoundManager is resumed
    sleep(10)
    #[TEARDOWN]: SoundManager stops the track
    print("pause")
    sound_mgr.delay()
    sound_mgr.pause()

def sound_manager_can_play_before_and_after_standby():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager standby")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager plays a track
    print("Playing track 1")
    sound_mgr.play(1)
    #[THEN]: SoundManager is playing the track
    sleep(10)
    #[WHEN]: SoundManager goes to standby
    print("standby")
    sound_mgr.standby()
    #[THEN]: SoundManager is stopped
    sleep(10)
    #[WHEN]: SoundManager plays a track
    print("Playing track 1")
    sound_mgr.play(1)
    #[THEN]: SoundManager is playing the track
    sleep(10)
    #[TEARDOWN]: SoundManager stops the track
    sound_mgr.standby()

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

def sound_does_not_play_when_device_has_idled_out():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager idle")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager is not called for a long time
    sleep(360)
    print("was idle for 6 minutes")
    #[THEN]: SoundManager is no longer playing the track
    sound_mgr.play(1)
    sleep(10)

def sound_manager_can_be_woken_up():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager wake up")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager is woken up
    sound_mgr.wake_up()
    #[THEN]: SoundManager is resumed
    sound_mgr.play(1)
    sleep(10)
    #[TEARDOWN]: SoundManager stops the track
    sound_mgr.standby()