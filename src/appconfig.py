'''
appconfig.py
Contains parameter settings for the application
'''
# WiFi credentials
wifi_ssid = 'Replace with the SSID'
wifi_pwd = 'Replace eith he SSID password'

# Log parameters
APPLOG_DEFAULT_MSGSTACK_SIZE = 20
APPLOG_LOGFILE = "app.log"

#Network connected led
wifi_connected_pin = 15

#WebServer parameters
listen_port = 80

#DHT11 Sensor PIN
dht11_pin = 28
DHT11_POLL_INTERVALL= 6 #seconds

#MQTT parameters
MQTT_BROKER = "io.adafruit.com" # MQTT broker IP address or DNS  
MQTT_PORT = 1883
MQTT_SUBSCRIBE_TOPIC = b"Replace with the topic"
MQTT_PUBLISH_TOPIC = b"Replace with the topic"
MQTT_USERNAME = "Replace with the username"
MQTT_PASSWORD = "Replace with the password"
