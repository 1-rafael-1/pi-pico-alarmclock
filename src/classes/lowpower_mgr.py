import drivers.lowpower as lowpower

class LowPowerManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        green_pin=state_mgr.button_green_pin()
        blue_pin=state_mgr.button_blue_pin()
        yellow_pin=state_mgr.button_yellow_pin()
        is_lowpower_mode = False

    def enter_lowpower_mode(self):
        self.state_mgr.deinit()
        is_lowpower_mode = True
        print("Entering lowpower mode...")
        print(f"Pins are: {green_pin}, {blue_pin}, {yellow_pin}")
        lowpower.dormant_until_pins([green_pin, blue_pin, yellow_pin])
        is_lowpower_mode = False
        self.state_mgr.initialize()