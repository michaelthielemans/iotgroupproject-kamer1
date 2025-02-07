import paho.mqtt.client as mqtt
import time
import time
import threading
import json

value = 0
received_value_field1 = 0

def on_connect(mqttc, obj, flags, reason_code, properties):
    print("reason_code: "+str(reason_code))

def on_message(mqttc, obj, msg):
    global received_value_field1
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    data = json.loads(msg.payload)
    
    # Extract field7 as integers
    received_value_field1 = int(float(data.get('field1', 0)))

def on_subscribe(mqttc, obj, mid, reason_code_list, properties):
    print("Subscribed: "+str(mid)+" "+str(reason_code_list))

def on_log(mqttc, obj, level, string):
    print(string)

#----- start mqtt connection ----#
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ChgAGx0oCSk4BycVPCANAzQ")
mqttc.username_pw_set("ChgAGx0oCSk4BycVPCANAzQ", "k/PbFlQ5JzYrB/bZxk/WfP3L")
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
        value += 1
        print("\n")
        print(f"+++--- The current value counter  =  {value} ---+++")
        print(f"+++--- The received value  =  {received_value_field1} ---+++")
        print("\n")
        # publish required temp to thingspeak
        payload= "field1=" + str(value)
        mqttc.publish("channels/2792381/publish", payload)

        time.sleep(20)

except KeyboardInterrupt:
    print("Exiting program...")

mqttc.loop_stop()
mqttc.disconnect()