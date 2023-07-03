'''
mqtt_client.py
Send MQTT-messages to a MQTT broker service (AdaFruit)
'''

import time
import ubinascii
from simple2 import MQTTClient
import machine

import appconfig as params
from applog import APPLOG
import dht11

class MQTT_CLIENT:
    def __init__(self, log:APPLOG, dht11: dht11.DHT11):
        self._log = log
        self._dht11 = dht11

        self._CLIENT_ID = ubinascii.hexlify(machine.unique_id()) #To create an MQTT client, we need to get the PICOW unique ID

     
        self._poll_interval = 30 #seconds read mesure interval
        self._publish_interval = 60 #seconds  publish to Adafruit interval
        self._last_publish = time.time() - self._publish_interval # last_publish variable will hold the last time a message was sent.
        self._mqtt_server_connected = False



    # Received messages from subscriptions will be delivered to this callback
    def sub_cb(self, topic, msg):
        led = machine.Pin("LED",machine.Pin.OUT)
        print((topic, msg))
        if msg.decode() == "ON":
            led.value(1)
        else:
            led.value(0)


    def mqtt_connect(self):
        # Default  MQTT_BROKER to connect to
        self._mqttClient = MQTTClient(self._CLIENT_ID, params.MQTT_BROKER, params.MQTT_PORT, \
                                params.MQTT_USERNAME, params.MQTT_PASSWORD, keepalive=60, ssl=False, ssl_params={})
        self._mqttClient.set_callback(self.sub_cb) # whenever a new message comes (to picoW), print the topic and message (The call back function will run whenever a message is published on a topic that the PicoW is subscribed to.)
        self._mqttClient.connect()
        #mqttClient.subscribe(params.MQTT_SUBSCRIBE_TOPIC)
        self._log.log_msg(APPLOG.INFO, "Connected with MQTT broker: {}".format(params.MQTT_BROKER))
        self._log.log_msg(APPLOG.DEBUG, "Measure intervals:  poll: {} seconds, publish: {} seconds" \
                    .format(self._poll_interval, self._publish_interval))
        self._mqtt_server_connected = True


    def mqtt_publish(self):
        self._log.log_msg(APPLOG.TRACE, 'Entering mqtt_publish dht11 is {}'.format(type(dht11)))

        if (not self._mqtt_server_connected):
            self.mqtt_connect() # Open a connection to Adafruit

        now = time.time()
        published_period = now - self._last_publish
        if (published_period < self._publish_interval):
            return

        temp = 0
        humidity = 0
        ts = ""
        try:
            (temp, humidity, ts) = self._dht11.measures
            self._log.log_msg(APPLOG.TRACE, "ts={} temp={}, humidity={}%".format(ts, temp, humidity))
        except Exception as e:
                self._log.log_msg(APPLOG.ERROR, str(e))

        if (temp > 0):
            self._mqttClient.publish(params.MQTT_PUBLISH_TOPIC, str(temp).encode())
            self._log.log_msg(APPLOG.DEBUG, "Published temp={}, humidity={}%".format(temp, humidity))
            self._last_publish = time.time()
