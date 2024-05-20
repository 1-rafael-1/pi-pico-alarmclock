import micropython
import ujson
from machine import Timer, RTC
import urequests

class TimeManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        self.update_rtc_timer = None

    def initialize(self):
        self.connect_wifi_and_update_rtc()
        
    def start_update_rtc_timer(self):
        if self.update_rtc_timer is None:
            self.state_mgr.log_emit("Starting update RTC timer", self.__class__.__name__)
            self.update_rtc_timer = Timer(period=3600000, mode=Timer.PERIODIC, callback=lambda a: self.connect_wifi_and_update_rtc())

    def stop_update_rtc_timer(self):
        if self.update_rtc_timer is not None:
            self.state_mgr.log_emit("Stopping update RTC timer", self.__class__.__name__)
            self.update_rtc_timer.deinit()
            self.update_rtc_timer = None

    @micropython.native
    def get_url(self):
        with open("settings//time_api.json", encoding="utf8") as file:
            data = ujson.load(file)
            url = data["time api by zone"]["baseurl"] + data["time api by zone"]["timezone"]
        return url

    @micropython.native
    def get_data(self):
        url = self.get_url()
        self.state_mgr.log_emit(f"making web request to: {url}", self.__class__.__name__)
        response = urequests.get(url)
        data = ujson.loads(response.text)
        response.close()
        self.state_mgr.log_emit(f"Time data fetched: {data}", self.__class__.__name__)
        return data

    @micropython.native
    def compose_data(self, data):
        year = data["year"]
        month = data["month"]
        day = data["day"]
        weekday = data["dayOfWeek"]
        hour = data["hour"]
        minute = data["minute"]
        second = data["seconds"]
        millisecond = data["milliSeconds"]
        weekday = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7
        }[weekday]
        return (year, month, day, weekday, hour, minute, second, millisecond)

    @micropython.native
    def connect_wifi_and_update_rtc(self):
        self.state_mgr.log_emit("Updating RTC", self.__class__.__name__)

        self.state_mgr.wifi_connect_wifi(max_wait=20, indicator=True)
        # we must must make sure we have a network connection, urequests has no timeout and will freeze the device	
        if not self.state_mgr.wifi_is_network_up():
            self.state_mgr.log_emit("No network connection", self.__class__.__name__)
            return
        
        self.update_rtc()
        self.state_mgr.wifi_disconnect_wifi(indicator=True)

    @micropython.native
    def update_rtc(self):
        try:
            data = self.get_data()
            rtc = RTC()
            rtc.datetime(self.compose_data(data))
            self.state_mgr.log_emit("RTC updated", self.__class__.__name__)
        except Exception as e:
            self.state_mgr.log_emit("Error updating RTC: {}".format(e), self.__class__.__name__)

    def deinit(self):
        self.stop_update_rtc_timer()