from drivers.picodfplayer import DFPlayer
from utime import sleep

class SoundManager:
    def __init__(self, state_mgr):
        self.player = DFPlayer(uartInstance=0, txPin=0, rxPin=1, busyPin=27)
        self.state_mgr = state_mgr

    def initialize(self):
        self.standby()

    def standby(self):
        self.player.standby()

    def reset(self):
        self.player.reset()

    def normal_mode(self):
        self.player.normalWorking()

    def set_playback_mode(self, mode):
        self.player.setPlaybackMode(mode)

    def play(self, folder, track):
        self.player.playTrack(folder=folder, file=track)

    def pause(self):
        self.player.pause()

    def resume(self):
        self.player.resume()

    def set_eq(self, eq):
        self.player.setEQ(eq)

    def set_volume(self, volume):
        self.player.setVolume(volume)

    def query_busy(self):
        return self.player.queryBusy()
    
    def alarm_sequence(self):
        print("Playing alarm sequence")
        self.set_eq(4) # classic
        self.set_volume(10) # medium volume
        self.play(1, 1) # play track 1 from folder 1
        sleep(3) # wait for track to start playing

    def alarm_stop(self):
        print("Stopping alarm sequence")
        self.pause() # stop the alarm

    def deinit(self):
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
    sound_mgr.reset()
    sound_mgr.set_volume(5)
    #[WHEN]: SoundManager plays a track
    sound_mgr.play(1, 1)
    #[THEN]: SoundManager is playing the track
    sleep(10)
    #[WHEN]: SoundManager pauses the track
    sound_mgr.pause()
    #[THEN]: SoundManager is paused
    sleep(10)
    #[WHEN]: SoundManager resumes the track
    sound_mgr.resume()
    #[THEN]: SoundManager is resumed
    sleep(10)
    #[TEARDOWN]: SoundManager stops the track
    sound_mgr.pause()

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
    sound_mgr.play(1, 1)
    sleep(10)

def sound_manager_can_be_woken_up():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager wake up")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager is woken up
    sound_mgr.normal_mode()
    #[THEN]: SoundManager is resumed
    sound_mgr.play(1, 1)
    sleep(10)
    #[TEARDOWN]: SoundManager stops the track
    sound_mgr.standby()

def run_tests():
    sound_manager_runs()
    sound_manager_alarm_sequence_can_start_and_stop()
    sound_does_not_play_when_device_has_idled_out()
    sound_manager_can_be_woken_up()
    print("All tests passed")