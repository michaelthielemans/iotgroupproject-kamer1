import paho.mqtt.client as mqtt
import json
from time import sleep
from gpiozero import Button

button1 = Button(9)
button2 = Button(2)
button3 = Button(3)
button4 = Button(4)
button5 = Button(5)
button6 = Button(6)
button7 = Button(7)
button8 = Button(8)

required_values = { 
    "kamer1": 0,
    "kamer2": 0,
    "kamer3": 0,
    "kamer4": 0,
    "kamer5": 0,
    "kamer6": 0,
    "kamer7": 0,
    "kamer8": 0
}

def increment_value(key):
    required_values[key] += 1
    print(f"The value of the button is now:   {key} value: {required_values[key]}")

button1.when_pressed = lambda: increment_value("kamer1")
button2.when_pressed = lambda: increment_value("kamer2")
button3.when_pressed = lambda: increment_value("kamer3")
button4.when_pressed = lambda: increment_value("kamer4")
button5.when_pressed = lambda: increment_value("kamer5")
button6.when_pressed = lambda: increment_value("kamer6")
button7.when_pressed = lambda: increment_value("kamer7")
button8.when_pressed = lambda: increment_value("kamer8")

def on_connect(mqttc, obj, flags, reason_code):
    print("reason_code: "+str(reason_code))

def on_message(mqttc, obj, msg):
    global required_value_kamer1
    print("\n")
    print("----New message received: ---- \n")
    #print(str(msg.payload))
    data = json.loads(msg.payload)
    print("data in json format:\n")
    print(data)
    print('\n')
    
    # Extract field7 as integers
    required_values["kamer1"] = int(data.get('field1', 0))
    #required_values["kamer2"] = int(float(data.get('field2', 0)))
    #required_values["kamer3"] = int(float(data.get('field3', 0)))
    #required_values["kamer4"] = int(float(data.get('field4', 0)))
    #required_values["kamer5"] = int(float(data.get('field5', 0)))
    #required_values["kamer6"] = int(float(data.get('field6', 0)))
    #required_values["kamer7"] = int(float(data.get('field7', 0)))
    #required_values["kamer8"] = int(float(data.get('field8', 0)))
    print("This is the data in the required_values variable:"+str(required_values["kamer1"]))

def on_subscribe(mqttc, obj, mid, reason_code_list):
    print("Subscribed: "+str(mid)+" "+str(reason_code_list))

def on_log(mqttc, obj, level, string):
    print("this is a log message:   "+string)

#----- start mqtt connection ----#
mqttc = mqtt.Client(client_id="Ih07MxA3OTIUNQEKAy4ZLz0")
mqttc.username_pw_set("Ih07MxA3OTIUNQEKAy4ZLz0", "lNnWkjCo2KbwIVKGAeHrXf+9")
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
mqttc.on_log = on_log
mqttc.connect("mqtt3.thingspeak.com", 1883, 60)
mqttc.subscribe("channels/2792381/subscribe", 0)
mqttc.loop_start()


try:
    while True: # Main thread's
        
        # publish required temp to thingspeak
        payload = "field1=" + str(required_values["kamer1"]) + "&field2=" + str(required_values["kamer2"]) + "&field3=" + str(required_values["kamer3"]) + "&field4=" + str(required_values["kamer4"]) + "&field5=" + str(required_values["kamer5"]) + "&field6=" + str(required_values["kamer6"]) + "&field7=" + str(required_values["kamer7"]) + "&field8=" + str(required_values["kamer8"])
        mqttc.publish("channels/2792381/publish", payload)
        print("this is the payload published:     "+str(payload))
        sleep(20)

except KeyboardInterrupt:
    print("Exiting program...")

mqttc.loop_stop()
mqttc.disconnect()