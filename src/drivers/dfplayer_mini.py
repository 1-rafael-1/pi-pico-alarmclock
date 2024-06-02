# taken from https://github.com/tomdionysus/dfplayermini-micropython
# modified to choose uart instance
# fixed missing import of utime
# fixed accessing class-level constants
# fixed missing method validate_checksum
# fixed missing constants
# added option to control power to the module
# added option to check if the module is busy

import machine
import utime

class DFPlayerMini:

    # Start and End Bytes
    START_BYTE = 0x7E
    END_BYTE = 0xEF
    VERSION_BYTE = 0xFF

    # Command Codes
    CMD_PLAY = 0x0D
    CMD_PAUSE = 0x0E
    CMD_NEXT = 0x01
    CMD_PREV = 0x02
    CMD_PLAY_TRACK = 0x03
    CMD_INC_VOLUME = 0x04
    CMD_DEC_VOLUME = 0x05
    CMD_SET_VOLUME = 0x06
    CMD_SET_EQ = 0x07
    CMD_REPEAT_TRACK = 0x08
    CMD_SET_PLAYBACK_SRC = 0x09
    CMD_SLEEP_MODE = 0x0A
    CMD_WAKE_UP = 0x0B
    CMD_RESET = 0x0C
    CMD_PLAY_FOLDER_FILE = 0x0F
    CMD_VOLUME_ADJUST_SET = 0x10
    CMD_REPEAT_PLAY = 0x11
    CMD_PLAY_FOLDER = 0x17
    CMD_SHUFFLE_PLAY = 0x18
    CMD_PLAY_ADVERT = 0x13
    CMD_STOP_ADVERT = 0x15
    CMD_STOP = 0x16
    CMD_QUERY_STATUS = 0x42
    CMD_QUERY_VOLUME = 0x43
    CMD_QUERY_EQ = 0x44
    CMD_QUERY_PLAYBACK_MODE = 0x45

    # Feedback Types
    FEEDBACK_REPLY = 0x41
    FEEDBACK_ERROR = 0x40
    FEEDBACK_INIT_COMPLETE = 0x3F
    FEEDBACK_STATUS = 0x42
    FEEDBACK_VOLUME = 0x43
    FEEDBACK_EQ = 0x44
    FEEDBACK_PLAYBACK_MODE = 0x45
    FEEDBACK_VERSION = 0x46
    FEEDBACK_TOTAL_FILES_TF = 0x47
    FEEDBACK_KEEP_ON = 0x4A
    FEEDBACK_CURRENT_TRACK_TF = 0x4C
    FEEDBACK_CURRENT_TRACK_USB = 0x4D
    FEEDBACK_TOTAL_TRACKS_FOLDER = 0x4E
    FEEDBACK_TOTAL_TRACKS = 0x4F
    FEEDBACK_TOTAL_FOLDERS = 0x50

    # Specific Feedback Command Codes for Track Finished and Device Status
    TRACK_FINISHED_UDISK = 0x3C  # U-Disk track finished
    TRACK_FINISHED_TF = 0x3D     # TF Card track finished
    DEVICE_STATUS = 0x3A         # Device status (insertion, removal)

    # Event Parameters for Device Status (Used with DEVICE_STATUS)
    DEVICE_USB_INSERTED = 0x01   # USB inserted
    DEVICE_TF_INSERTED = 0x02    # TF card inserted
    DEVICE_USB_REMOVED = 0x01    # USB removed
    DEVICE_TF_REMOVED = 0x02     # TF card removed

    # Error Codes
    ERROR_BUSY = 0x01
    ERROR_SLEEPING = 0x02
    ERROR_SERIAL_WRONG_STACK = 0x03
    ERROR_CHECKSUM_NOT_MATCH = 0x04
    ERROR_FILE_INDEX_OUT = 0x05
    ERROR_FILE_MISMATCH = 0x06
    ERROR_ADVERTISE = 0x07

    # EQ Modes
    EQ_NORMAL = 0
    EQ_POP = 1
    EQ_ROCK = 2
    EQ_JAZZ = 3
    EQ_CLASSIC = 4
    EQ_BASIC = 5

    # Playback Source
    SRC_U_DISK = 1
    SRC_SD = 2
    SRC_AUX = 3
    SRC_SLEEP = 4
    SRC_FLASH = 5

    # Playback Modes
    MODE_REPEAT = 0
    MODE_FOLDER_REPEAT = 1
    MODE_SINGLE_REPEAT = 2
    MODE_RANDOM = 3

    # Initialization: Setting up serial communication.

    def __init__(self, tx_pin, rx_pin, uartinstance=1, power_pin=None, busy_pin=None, txbuf=32, rxbuf=32, timeout=10, timeout_char=10, bits=8):
        self.uart = machine.UART(uartinstance, baudrate=9600, tx=tx_pin, rx=rx_pin)
        if power_pin is not None:
            self.power_pin = machine.Pin(power_pin, machine.Pin.OUT)
        if busy_pin is not None:
            self.busy_pin = machine.Pin(busy_pin, machine.Pin.IN)
            
    def power_on(self):
        """
        Power on the DFPlayer Mini module. Requires a hardware power switch, using a GPIO pin and a MOSFET. Do NOT power the device from the GPIO pin directly!
        """
        if hasattr(self, 'power_pin'):
            self.power_pin.on()

    def power_off(self):
        """
        Power off the DFPlayer Mini module. equires a hardware power switch, using a GPIO pin and a MOSFET. Do NOT power the device from the GPIO pin directly!
        """
        if hasattr(self, 'power_pin'):
            self.power_pin.off()
    
    def begin(self):
        """
        Initialize communication with the DFPlayer Mini module.
        Call this method before performing any operations with the module.
        """
        self.wait_for_ready()

    def wait_for_ready(self):
        """
        Waits until the module is ready after power on.
        """
        # Wait for a specific time for DFPlayer Mini to initialize
        utime.sleep_ms(500)

    def is_busy(self):
        """
        Check if the DFPlayer Mini is busy.

        :return: True if the module is busy, False otherwise.
        """
        if hasattr(self, 'busy_pin'):
            return self.busy_pin.value() == 0 # low means busy
        return False

    # Sending Commands: General method to construct and send command packets.

    def send_command(self, command, parameter=0):
        """
        Sends a command to the DFPlayer Mini.

        :param command: The command byte.
        :param parameter: The parameter for the command, default to 0.
        """
        param_high = parameter >> 8
        param_low = parameter & 0xFF
        checksum = self.calculate_checksum(command, param_high, param_low)
        checksum_high = checksum >> 8
        checksum_low = checksum & 0xFF
        command_packet = bytearray([self.START_BYTE, self.VERSION_BYTE, 0x06, command, 0x00, param_high, param_low, checksum_high, checksum_low, self.END_BYTE])
        self.uart.write(command_packet)
        #print("Sent command: ", command_packet) 
        #self.uart.flush()
        i = 0
        while not self.uart.txdone():
            i += 1
            utime.sleep_ms(10)
        #print("Flushed UART after ", i, " attempts.")

    def calculate_checksum(self, command, param_high, param_low):
        """
        Calculates the checksum for a given command and parameter.

        :param command: The command byte.
        :param param_high: High byte of the parameter.
        :param param_low: Low byte of the parameter.
        :return: The calculated checksum.
        """
        checksum = -(self.VERSION_BYTE + 0x06 + command + 0x00 + param_high + param_low)
        return checksum & 0xFFFF

    def validate_checksum(self, response):
        """
        Validates the checksum in the response.
        :param response: The response data.
        :return: True if the checksum is valid, False otherwise.
        """
        # Extract the checksum from the response
        response_checksum = (response[7] << 8) | response[8]

        # Calculate the checksum of the command and parameters
        calculated_checksum = -sum(response[1:7]) & 0xFFFF

        # Compare the two checksums
        return response_checksum == calculated_checksum

    # Playing Tracks: Play a specific track, play next/previous.

    def play_track(self, track_number):
        """
        Play a specific track.

        :param track_number: Track number to play.
        """
        self.send_command(self.CMD_PLAY_TRACK, track_number)

    def play_next(self):
        """
        Play the next track.
        """
        self.send_command(self.CMD_NEXT)

    def play_previous(self):
        """
        Play the previous track.
        """
        self.send_command(self.CMD_PREV)

    # Volume Control: Set volume, increase/decrease volume.

    def set_volume(self, volume):
        """
        Set the volume level.

        :param volume: Volume level (0-30).
        """
        self.send_command(self.CMD_SET_VOLUME, volume)

    def volume_up(self):
        """
        Increase the volume by one level.
        """
        self.send_command(self.CMD_INC_VOLUME)

    def volume_down(self):
        """
        Decrease the volume by one level.
        """
        self.send_command(self.CMD_DEC_VOLUME)

    # Playback Control: Pause, resume, stop.

    def pause(self):
        """
        Pause playback.
        """
        self.send_command(self.CMD_PAUSE)

    def resume(self):
        """
        Resume playback.
        """
        self.send_command(self.CMD_PLAY)

    def stop(self):
        """
        Stop playback.
        """
        self.send_command(self.CMD_STOP)

    # Querying Status: Get the current status of the player.

    def read_response(self):
        start_time = utime.ticks_ms()
        while not self.uart.any():
            # Break the loop if no response is received within a timeout period (e.g., 2000 ms)
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 2000:
                return "Timeout Error"
            utime.sleep_ms(10)  # Wait a bit before checking again

        response = self.uart.read(10)
        if len(response) == 10 and response[0] == self.START_BYTE and response[9] == self.END_BYTE:
            if self.validate_checksum(response):
                return response[6]  # The status byte
            else:
                return "Checksum Error"
        else:
            return "Invalid Response"
    
    def get_status(self):
        """
        Get the current status of the player.
        """
        self.send_command(self.CMD_QUERY_STATUS)
        return self.read_response()
    
    def get_current_volume(self):
        """
        Get the current volume level.
        """
        self.send_command(self.CMD_QUERY_VOLUME) 
        return self.read_response()
    
    def get_current_eq(self):
        """
        Get the current equalizer mode.
        """
        self.send_command(self.CMD_QUERY_EQ)
        return self.read_response()
    
    def get_playback_mode(self):
        """
        Get the current playback mode.
        """
        self.send_command(self.CMD_QUERY_PLAYBACK_MODE)
        return self.read_response()

    # Feedback Handling: Process feedback from the device, like track finished, error messages.

    def poll_feedback(self):
        """
        Polls the device for feedback, processing any available data.
        """
        if self.uart.any():
            response = self.uart.read(10)
            if len(response) == 10 and response[0] == self.START_BYTE and response[9] == self.END_BYTE:
                if self.validate_checksum(response):
                    return response[3], response[6]
                else:
                    return "Checksum Error"
            else:
                return "Invalid Response"
        return None

    # Advanced Playback Options: Repeat, shuffle, play from a specific folder.

    def repeat_track(self, track_number):
        """
        Repeat a specific track.

        :param track_number: Track number to repeat.
        """
        self.send_command(self.CMD_REPEAT_TRACK, track_number)

    def play_from_folder(self, folder_number, track_number):
        """
        Play a specific track from a specific folder.

        :param folder_number: Folder number.
        :param track_number: Track number in the folder.
        """
        # Combine folder and track number into one parameter
        parameter = (folder_number << 8) | track_number
        self.send_command(self.CMD_PLAY_FOLDER_FILE, parameter)

    def shuffle_play(self):
        """
        Enable shuffle playback.
        """
        self.send_command(self.CMD_SHUFFLE_PLAY)

    # Utility Functions: Reset, sleep, and other utility controls.

    def reset(self):
        """
        Reset the DFPlayer Mini module.
        """
        self.send_command(self.CMD_RESET)
        self.wait_for_ready()

    def sleep(self):
        """
        Put the DFPlayer Mini into sleep mode.
        """
        self.send_command(self.CMD_SLEEP_MODE)

    def wake_up(self):
        """
        Wake the DFPlayer Mini from sleep mode.
        """
        self.send_command(self.CMD_WAKE_UP)

    def set_playback_source(self, source):
        """
        Set the playback source.

        :param source: The source (e.g., SD card, USB).
        """
        self.send_command(self.CMD_SET_PLAYBACK_SRC, source)

    def set_equalizer(self, eq_mode):
        """
        Set the equalizer mode.

        :param eq_mode: Equalizer mode (e.g., rock, pop, jazz).
        """
        self.send_command(self.CMD_SET_EQ, eq_mode)

    def set_volume_adjustment(self, gain):
        """
        Set the volume adjustment.

        :param gain: Gain value.
        """
        self.send_command(self.CMD_VOLUME_ADJUST_SET, gain)

    def repeat_play(self, enable):
        """
        Set repeat play.

        :param enable: Enable or disable repeat.
        """
        self.send_command(self.CMD_REPEAT_PLAY, 0x01 if enable else 0x00)
