from machine import Pin, ADC, mem32

class PowerManager:
    def __init__(self, state_mgr, lower_bound=2.5, upper_bound=4.0):
        self.state_mgr = state_mgr
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.conversion_factor = 3.3 / 65535
        self.vsys_voltage = 0
        self.temperature = 0
        
    def initialize(self):
        self.read_vsys()

    def get_battery_state(self):
        if self.vsys_voltage >= self.upper_bound:
            return "Charging"
        elif self.vsys_voltage < self.lower_bound:
            return "Error"
        else:
            return "Normal"

    def get_battery_charge_percentage(self):
        if self.vsys_voltage >= self.upper_bound:
            return 100
        elif self.vsys_voltage < self.lower_bound:
            return 0
        else:
            return int((self.vsys_voltage - self.lower_bound) * 100 / (self.upper_bound - self.lower_bound))
        
    def is_usb_powered(self):
        vbus = Pin("WL_GPIO2", Pin.IN)
        return vbus.value()
    
    def get_pad(self, gpio):
        return mem32[0x4001c000 | (4+ (4 * gpio))]
    
    def det_pad(self, gpio, value):
        mem32[0x4001c000 | (4+ (4 * gpio))] = value

    def read_vsys(self):
        oldpad = self.get_pad(29)
        self.det_pad(29,128)  #no pulls, no output, no input
        adc_vsys = ADC(3)
        vsys = adc_vsys.read_u16() * 3.0 * self.conversion_factor
        self.det_pad(29,oldpad)
        self.vsys_voltage = vsys

    def read_temperature(self):
        sensor_temp = ADC(4)
        conversion_factor = 3.3 / (65535)
        reading = sensor_temp.read_u16() * conversion_factor
        self.temperature = round((27 - (reading - 0.706)/0.001721), 2)

    def get_temperature(self):
        return self.temperature
    
    def get_vsys_voltage(self):
        return self.vsys_voltage

    def log_vsys(self):
        self.read_vsys()
        self.state_mgr.log_emit(f"VSYS voltage: {self.vsys_voltage}", self.__class__.__name__)

## Tests

def test_power_manager():
    power = PowerManager()
    power.read_vsys()
    power.read_temperature()
    print('Battery state:', power.get_battery_state())
    print('Battery charge percentage:', power.get_battery_charge_percentage())
    print('USB powered:', power.is_usb_powered())
    print('Temperature:', power.get_temperature())
    