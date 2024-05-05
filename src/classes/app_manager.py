import micropython
from utime import sleep
from machine import idle, freq, lightsleep
from classes.state_mgr import StateManager

class ApplicationManager:
    def __init__(self):
        self.state_manager = StateManager()

    @micropython.native
    def initialize(self):
        print("Initializing...")
        self.state_manager.initialize()
        print("Initialization complete")

    @micropython.native
    def run(self):
        try:
            print("Entering main loop...")
            while True:
                idle()    
                sleep(.01)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An unexpected error occurred: ", e)
        finally:
            print("Closing...")

    def stop(self):
        print("Closing...")
        self.state_manager.deinit()