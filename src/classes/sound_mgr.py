from drivers.dfplayer_mini import DFPlayerMini
from utime import sleep
from machine import Pin

class SoundManager:
    def __init__(self, state_mgr):
        self.player = DFPlayerMini(uartinstance=1, tx_pin=4, rx_pin=5, power_pin=8, busy_pin=3)
        self.io1 = Pin(2, Pin.OUT)
        self.io2 = Pin(3, Pin.OUT)
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

    def get_status(self):
        return self.player.get_status()
    
    def poll_feedback(self):
        return self.player.poll_feedback()

    def power_on(self):
        self.state_mgr.log_emit("Powering on", self.__class__.__name__)
        self.io1.on() #drivnig high to not ground
        self.io2.on() #driving high to not ground
        self.player.power_on()

    def power_off(self):
        self.state_mgr.log_emit("Powering off", self.__class__.__name__)
        self.player.power_off()

    def alarm_start(self):
        self.state_mgr.log_emit("Playing alarm sequence", self.__class__.__name__)
        self.power_on()

    def alarm_stop(self):
        self.state_mgr.log_emit("Stopping alarm sequence", self.__class__.__name__)
        self.power_off()

    def deinit(self):
        self.delay()
        self.power_off()

    def play_by_io(self):
        # play by io, very(!) stupid thing to do
        self.state_mgr.log_emit("Playing by io", self.__class__.__name__)
        self.io1.off()
        sleep(0.6)
        self.io2.on()

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
def sound_manager_can_power_on_and_off_staying_quiet():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager power on/off")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager powers on the device
    sound_mgr.power_on()
    #[THEN]: SoundManager is powered on
    sleep(10)
    #[WHEN]: SoundManager powers off the device
    sound_mgr.power_off()
    #[THEN]: SoundManager is powered off

def sound_manager_can_power_on_and_play_a_track():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager play track")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager powers on the device
    sound_mgr.power_on()
    #[THEN]: SoundManager is powered on
    sleep(1)
    #[WHEN]: we initiate play by io
    sound_mgr.play_by_io()
    #[THEN]: we play a track
    sleep(20)
    #[TEARDOWN]: SoundManager powers off the device
    sound_mgr.power_off()

def sound_manager_alarm_sequence_can_start_and_stop():
    #[GIVEN]: SoundManager instance
    print("Test SoundManager alarm sequence")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    #[WHEN]: SoundManager starts the alarm sequence
    sound_mgr.alarm_start()
    #[THEN]: SoundManager is playing the alarm sequence
    sleep(10)
    #[WHEN]: SoundManager stops the alarm sequence
    sound_mgr.alarm_stop()
    #[THEN]: SoundManager is stopped

def we_get_sane_states_from_the_sound_device():
    #[GIVEN]: SoundManager instance, no power to the device
    print("Test SoundManager status")
    state_mgr = MockStateManager()
    sound_mgr = SoundManager(state_mgr)
    sound_mgr.power_off()
    #[WHEN]: SoundManager polls the status
    status = sound_mgr.get_status()
    #[THEN]: we get no status at all
    print("Before powering on: Status is " + str(status))
    assert status == None, "Expected status to be None, but got " + str(status)
    #[WHEN]: SoundManager powers on the device
    sound_mgr.power_on()
    #[THEN]: we get a status 0
    status = sound_mgr.get_status()
    print("After powering on: Status is " + str(status))
    assert status == 0, "Expected status to be 0, but got " + str(status)
    #[WHEN]: we have set the equalizer
    sound_mgr.set_eq(4)
    #[THEN]: we get a status 0
    status = sound_mgr.get_status()
    print("After setting equalizer: Status is " + str(status))
    assert status == 0, "Expected status to be 0, but got " + str(status)
    #[WHEN]: we have set the volume
    sound_mgr.set_volume(10)
    #[THEN]: we get a status 0
    status = sound_mgr.get_status()
    print("After setting volume: Status is " + str(status))
    assert status == 0, "Expected status to be 0, but got " + str(status)
    #[TEARDOWN]: SoundManager powers off the device
    sound_mgr.power_off()