'''
network.py
Manages connection to WiFi network
'''
import machine
import network
from time import sleep

import appconfig as params
from applog import APPLOG


class NETCONN:
    _ip_address = None # IP-address of the established connection
    _netconn_led = None # Led that lights when the network is connected

    def __init__(self, log:APPLOG):
        self._log = log

    # Returns True if there is an established connection 
    def is_connected(self):
        wlan = network.WLAN(network.STA_IF)
        return wlan.isconnected()


    def wifi_connect(self):
        wlan = network.WLAN(network.STA_IF) # Connect as a station interface. STA_IF meaning as any other device that normally connects to it.
        self._netconn_led = machine.Pin(params.wifi_connected_pin, machine.Pin.OUT)

        self._log.log_msg(APPLOG.TRACE, "isconnected=" + str(wlan.isconnected()))
        if (wlan.isconnected() == False):
            wlan.active(True) # Turns on the wifi-interface
            wlan.connect(params.wifi_ssid, params.wifi_pwd)		# Ask the interaface to connect to the network whose ssid is provided, with the provided password.
            loop_count = 0
            while wlan.isconnected() == False:	# While the interface is not connected, print message and wait for 1 sec, do this until it is connected
                wstat = wlan.status()
                loop_count += 1
                if (loop_count > 60):
                    self._log.log_msg(APPLOG.FATAL, "No WLAN connection status={}".format(wstat))
                    machine.reset()

                if (loop_count % 5 == 0):
                    self._log.log_msg(APPLOG.DEBUG, 'Waiting for connection... status=' + str(wstat))
                    self._netconn_led.on();
                sleep(0.5)
                self._netconn_led.off();
                sleep(0.5)

        self._ip_address = wlan.ifconfig()[0]	# Sets the ip adress of the pico. Length of the array is four, where router ip is the last, and the pico adress is the first.
        self._netconn_led = machine.Pin(params.wifi_connected_pin, machine.Pin.OUT)
        self._netconn_led.on();
        self._log.log_msg(APPLOG.DEBUG, "IP:" + str(self._ip_address))
        return wlan
        
    def wifi_disconnect(self):
        try:
            if (self.is_connected() == True):
                wlan = network.WLAN(network.STA_IF) 
                wlan.disconnect()
                wlan.active(False)
                wlan.deinit()
        except Exception as e:
            self._log.log_msg(APPLOG.ERROR, "wifi_disconnect: " + str(e))
            self._log.log_msg(APPLOG.ERROR, type(e))

        try:
            netconn_led = machine.Pin(params.wifi_connected_pin, machine.Pin.OUT)
            netconn_led.off()
        except Exception as e:
            self._log.log_msg(APPLOG.ERROR, "wifi_disconnect (led): " + str(e))
            self._log.log_msg(APPLOG.ERROR, type(e))


    # Returns the network connection object 
    def connect(self):
        if (self.is_connected() == False):
            self.wifi_connect() # Connect to the network if not already done

        return network.WLAN(network.STA_IF)