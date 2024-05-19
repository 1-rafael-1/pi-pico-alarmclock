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
            print("app_mgr: Entering main loop...")
            while True:
                idle()
                
                if self.state_mgr.lowpower_is_lowpower_mode_active():
                    sleep(10)
                else:
                    sleep(.02)
        
                if self.state_mgr.menu_get_system_state() == "shutdown":
                    self.state_mgr.display_compose()
                    sleep(2)
                    self.state_mgr.lowpower_enter_lowpower_mode()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("An unexpected error occurred in app_mgr.py: ", e)
        finally:
            print("Closing...")

    def stop(self):
        print("Closing...")
        self.state_mgr.deinit()