import micropython
from utime import sleep
from machine import idle, lightsleep
from classes.state_mgr import StateManager

class ApplicationManager:
    def __init__(self):
        self.state_mgr = StateManager()

    @micropython.native
    def initialize(self):
        print("Initializing...")
        self.state_mgr.initialize()
        print("Initialization complete")

    @micropython.native
    def run(self):
        try:
            print("Entering main loop...")
            while True:
                idle()
                if self.state_mgr.lowpower_is_lowpower_mode_active():
                    lightsleep(1000)
                else:
                    sleep(.01)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An unexpected error occurred in app_mgr.py: ", e)
        finally:
            print("Closing...")

    def stop(self):
        print("Closing...")
        self.state_mgr.deinit()