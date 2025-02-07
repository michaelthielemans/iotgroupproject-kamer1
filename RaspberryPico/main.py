import network
import socket
from time import sleep
from umqtt.simple import MQTTClient
import time
from machine import Pin

# WiFi credentials
ssid = 'telenet-8650069'
password = 'Gdssbyvfx6dj'

# MQTT Broker details (ThingSpeak)
MQTT_BROKER = "mqtt3.thingspeak.com"
ClientID = "Ih07MxA3OTIUNQEKAy4ZLz0"
user = "Ih07MxA3OTIUNQEKAy4ZLz0"
password = "lNnWkjCo2KbwIVKGAeHrXf+9"

# Topics
PUBLISH_TOPIC = b'channels/2792381/publish/fields/field1'
SUBSCRIBE_TOPIC = b'channels/2792381/subscribe'

field1_required_value = 1  # Start at 1

# The debounce time for buttons
DEBOUNCE_TIME = 200

class ButtonHandler:
    def __init__(self, pin, name, callback):
        """Initialize a button with debounce logic."""
        self.button = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.name = name
        self.callback = callback  # Function to call when button is pressed
        self.last_press_time = 0  # Track last press time
        
        # Attach interrupt to button press (falling edge)
        self.button.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.handle_press)

    def handle_press(self, pin):
        """IRQ handler with software debounce."""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_press_time) > DEBOUNCE_TIME:
            self.last_press_time = current_time  # Update press time
            self.callback(self.name)  # Call the user-defined callback

# User-defined callback function
def button_pressed(button_name):
    global field1_required_value
    print(f"🚀 {button_name} pressed!")
    if button_name == "Button A":
        field1_required_value += 1

# Define multiple buttons with their respective pins
button1 = ButtonHandler(11, "Button A", button_pressed)
button2 = ButtonHandler(12, "Button B", button_pressed)
button3 = ButtonHandler(13, "Button C", button_pressed)
button4 = ButtonHandler(14, "Button D", button_pressed)
button5 = ButtonHandler(15, "Button E", button_pressed)      

# MQTT Message Callback Function
def message_callback(topic, msg):
    print(f"📩 Received message on {topic.decode()}: {msg.decode()}")

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        print('Waiting for WiFi connection...')
        sleep(1)
    
    print("✅ Connected to WiFi:", wlan.ifconfig())
    return wlan

# Connect to MQTT Broker
def MQTT_connect():
    try:
        print(f'Connecting to MQTT Broker: {MQTT_BROKER}')
        client = MQTTClient(ClientID, MQTT_BROKER, 1883, user, password)
        client.set_callback(message_callback)
        client.connect()
        print("✅ MQTT Connected!")
        client.subscribe(SUBSCRIBE_TOPIC)
        print(f"📡 Subscribed to: {SUBSCRIBE_TOPIC.decode()}")
        return client
    except Exception as e:
        print('❌ MQTT Connection Failed:', e)
        raise

# Reconnect to MQTT Broker
def MQTT_reconnect():
    print('🔄 Reconnecting to MQTT Broker...')
    time.sleep(10)
    return MQTT_connect()

# Start WiFi & MQTT
wlan = connect_wifi()
addr = socket.getaddrinfo("mqtt3.thingspeak.com", 1883)
print("🌍 DNS resolved:", addr)

client = MQTT_connect()

# Main Loop (Publishing & Listening for Messages)
try:
    while True:
        # WiFi Reconnection Handling
        if not wlan.isconnected():
            print("⚠️ WiFi Disconnected! Reconnecting...")
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                print("Reconnecting...")
                time.sleep(1)
            print("✅ Reconnected to WiFi.")

        # Update field value as bytes
        field1_required_value_Byte = str(field1_required_value).encode()

        # Send MQTT Ping (Check Connection)
        try:
            print("--> Sending a ping to the broker")
            client.ping()
        except Exception as e:
            print("❌ MQTT Ping Failed. Reconnecting:", e)
            client = MQTT_reconnect()

        # Publish message
        print(f'📤 Sending message: {field1_required_value} to topic {PUBLISH_TOPIC}')
        #client.publish(PUBLISH_TOPIC, field1_required_value_Byte)
        client.publish(b'channels/2792381/publish/fields/field1', field1_required_value_Byte)
        # Listen for incoming messages
        print(f'Waiting for messages...')
        client.check_msg()  

        # Sleep before next loop
        print('--> Sleeping for 20 seconds...')
        time.sleep(20)

except Exception as e:
    print('❌ Error:', e)
    client = MQTT_reconnect()

finally:
    print("🛑 Disconnecting WiFi...")
    wlan.active(False)
    print("✅ WiFi Disconnected. Exiting Cleanly.")
