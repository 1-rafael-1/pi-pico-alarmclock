import drivers.lowpower as lowpower

class LowPowerManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        self.green_pin=state_mgr.button_green_pin()
        self.blue_pin=state_mgr.button_blue_pin()
        self.yellow_pin=state_mgr.button_yellow_pin()
        self.is_lowpower_mode = False

    def enter_lowpower_mode(self):
        self.state_mgr.deinit()
        self.is_lowpower_mode = True
        print("Entering lowpower mode...")
        print(f"pins are: {self.green_pin}, {self.blue_pin}, {self.yellow_pin}")
        lowpower.dormant_until_pins([self.green_pin, self.blue_pin, self.yellow_pin], edge=True, high=True)
        self.is_lowpower_mode = False
        self.state_mgr.initialize()