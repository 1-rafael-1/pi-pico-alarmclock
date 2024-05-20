import micropython
from utime import sleep, time
from machine import idle, lightsleep
from classes.state_mgr import StateManager

class ApplicationManager:
    def __init__(self):
        self.state_mgr = StateManager()
        self.set_logging_level()

    @micropython.native
    def set_logging_level(self):
        self.state_mgr.log_set_verbose(False)
        self.state_mgr.log_set_log(False)
        self.state_mgr.log_set_max_log_length(1000)
        self.state_mgr.log_set_log_file('log.txt')
        self.state_mgr.log_set_clean_log(False)

    @micropython.native
    def initialize(self):
        self.state_mgr.log_emit("Initializing app", self.__class__.__name__)
        self.state_mgr.initialize()
        self.state_mgr.log_emit("App initialized", self.__class__.__name__)

    @micropython.native
    def run(self):
        try:
            last_time = time()
            current_time = time()
            self.state_mgr.log_emit("Entering main loop", self.__class__.__name__)
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

                if self.state_mgr.log_get_log():
                    current_time = time()
                    if current_time - last_time >= 600:
                        self.state_mgr.power_log_vsys()
                        last_time = current_time
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.state_mgr.log_emit("An unexpected error occurred in app_mgr.py: " + str(e), self.__class__.__name__)
        finally:
            self.stop()

    def stop(self):
        self.state_mgr.log_emit("Exiting main loop", self.__class__.__name__)
        self.state_mgr.deinit()