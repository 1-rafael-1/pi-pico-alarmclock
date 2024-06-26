import json
import micropython
from utime import sleep 

from machine import Pin
from network import WLAN, STA_IF

import usocket

class WifiManager:
    def __init__(self, state_mgr):
        self.state_mgr = state_mgr
        self.indicator = Pin("LED", Pin.OUT)

    @micropython.native
    def secrets(self):
        try:
            with open("settings//wifi.json", encoding="utf8") as file:
                data = json.load(file)
                ssid = data["ssid"]
                password = data["password"]
            return ssid, password
        except Exception as e:
            self.state_mgr.emit("The settings/wifi.json file was not found. Please ensure it exists and is in the correct location.", self.__class__.__name__)

    @micropython.native
    def active_indicator(self, wlan):
        if wlan.isconnected():
            self.indicator.value(1)
        else:
            self.indicator.value(0)

    @micropython.native
    def connect(self, max_wait=20, indicator=True):
        wlan = WLAN(STA_IF)
        wlan.active(True)
        ssid, password = self.secrets()
        self.state_mgr.log_emit("Connecting to WiFi: " + ssid, self.__class__.__name__)
        wlan.connect(ssid, password)
        self.state_mgr.log_emit("Waiting for WLAN connection to succeed", self.__class__.__name__)
        while not wlan.isconnected() and max_wait > 0:
            sleep(1)
            max_wait -= 1
            self.state_mgr.log_emit(".", self.__class__.__name__)
        if not wlan.isconnected():
            self.state_mgr.log_emit("WLAN connection failed", self.__class__.__name__)
        if indicator:
            self.active_indicator(wlan)
        return wlan

    @micropython.native
    def disconnect(self, max_wait=20, indicator=True):
        self.state_mgr.log_emit("Disconnecting WLAN", self.__class__.__name__)
        wlan = WLAN(STA_IF)
        if indicator:
            self.active_indicator(wlan)
        wlan.active(False)
        wlan.deinit()

    @micropython.native
    def reconnect(self, max_wait=20):
        if not self.is_network_up():
            self.disconnect()
            wlan = self.connect(max_wait=max_wait)

    @micropython.native
    def is_network_up(self):
        addr = usocket.getaddrinfo("www.google.de", 80)[0][-1]
        s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        try:
            s.connect(addr)
            return True
        except:
            return False
        finally:
            s.close()

    def deinit(self):
        self.disconnect()

## Tests

def wifi_can_connect_and_disconnect():
    #[GIVEN]: A WifiManager instance
    wifi = WifiManager()
    #[WHEN]: Connecting to a network
    wifi.connect()
    #[THEN]: The network is connected
    assert wifi.is_network_up() == True, "Network is not connected"
    #[WHEN]: Disconnecting from the network
    wifi.disconnect()
    #[THEN]: The network is disconnected

def wifi_can_connect_after_disconnected():
    #[GIVEN]: A WifiManager instance
    wifi = WifiManager()
    #[WHEN]: Connecting to a network
    wifi.connect()
    #[THEN]: The network is connected
    assert wifi.is_network_up() == True, "Network is not connected"
    #[WHEN]: Disconnecting from the network
    wifi.disconnect()
    #[THEN]: The network is disconnected
    assert wifi.is_network_up() == False, "Network is still connected"
    #[WHEN]: Reconnecting to the network
    wifi.reconnect()
    #[THEN]: The network is connected
    assert wifi.is_network_up() == True, "Network is not connected"
    #[TEARDOWN]: Disconnecting from the network
    wifi.disconnect()