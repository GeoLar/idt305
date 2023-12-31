'''
main.py
 Main logic to start up the the PICO Microcontroller application. 
 When the PICO is started the bootloader executes main.py after boot.py.
'''
import machine
from machine import Pin
import ntptime
import time

from applog import APPLOG
import appconfig as params
import dht11
from mqtt_client import MQTT_CLIENT
from netconn import NETCONN
from webserver import WEBSERVER

# Allocate objects
log = APPLOG(log_level=APPLOG.INFO)
conn = NETCONN(log)
dht11_pin = Pin(params.dht11_pin, Pin.OUT, Pin.PULL_DOWN)
dht11 = dht11.DHT11(dht11_pin, log)
mqtt = MQTT_CLIENT(log, dht11=dht11)
webserver = WEBSERVER(log=log, conn=conn, dht11=dht11)


try:
    conn.wifi_connect() # Connect to a network

    try:
        if (time.time() < 1688586897):
            rtc = machine.RTC()
            log.log_msg(APPLOG.INFO,"Setting time... current time is " + str(rtc.datetime()), permanent=True)
            ntptime.settime()
            tm = time.localtime(time.time()+2*60*60)
            dttm = (tm[0],tm[1],tm[2], tm[6],tm[3],tm[4],tm[5],tm[7])
            rtc.datetime(dttm)
            log.log_msg(APPLOG.INFO,"Time set to " + str(rtc.datetime()), permanent=True)
    except Exception as e:
        log.log_msg(APPLOG.WARN, "'Can't set time: " + str(e), permanent=True) 

    # loop for ever,
    #   handle request to the webserver  
    #   and send measured values to the MQTT-service
    while True:
        time.sleep(0.5)
        webserver.serve() # Non blocking 
        mqtt.mqtt_publish() # Read mesaures and publish them in Adafruit
except KeyboardInterrupt as e: # Handles the ctrl+c command.
    log.log_msg(APPLOG.INFO, "Keyboard interupt: " + str(e))
except Exception as e: 
    log.log_msg(APPLOG.FATAL, "Exception main: " + str(e) + " " + str(type(e)))
    machine.reset() 
finally:
    try:
        webserver.close()
    except Exception as e:
        log.log_msg(APPLOG.ERROR, str(e))

    try:
        conn.wifi_disconnect()
    except Exception as e:
        log.log_msg(APPLOG.ERROR, str(e))

log.log_msg(log.DEBUG, "main done!")
		