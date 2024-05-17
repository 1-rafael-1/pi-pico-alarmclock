import micropython
from utime import sleep
from machine import idle, freq, lightsleep
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
            cntr = 0
            while True:
                idle()    
                sleep(.01)
                cntr += 1
                if cntr % 1000 == 0:
                    print("Running...")
                if cntr % 10000 == 0:
                    cntr = 0
                    print("Entering lowpower mode...")
                    self.state_mgr.lowpower_enter_lowpower_mode()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An unexpected error occurred: ", e)
        finally:
            print("Closing...")

    def stop(self):
        print("Closing...")
        self.state_mgr.deinit()