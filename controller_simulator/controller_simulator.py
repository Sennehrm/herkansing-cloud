import paho.mqtt.client as mqtt
import random, time
import json

MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
TOPIC_JOYSTICK1 = 'sensor/controller/joystick1'
TOPIC_JOYSTICK2 = 'sensor/controller/joystick2'
TOPIC_BUTTONS = 'sensor/controller/buttons'

mqttc = mqtt.Client()
mqttc.connect(MQTT_BROKER, MQTT_PORT)

while True:
    x1 = random.randint(0, 255)
    y1 = random.randint(0, 255)
    x2 = random.randint(0, 255)
    y2 = random.randint(0, 255)
    pressed_count = random.randint(0, 7)
    button_map = {
        0: "X",
        1: "B",
        2: "A",
        3: "Y",
        4: "R1",
        5: "L1",
        6: "R2",
        7: "L2"
    }
    button_name = button_map.get(pressed_count, "UNKNOWN")

    joystick_payload1 = json.dumps({
        "x": x1,
        "y": y1
    })
    joystick_payload2 = json.dumps({
        "x": x2,
        "y": y2
    })
    buttons_payload = json.dumps(button_name)

    mqttc.publish(TOPIC_JOYSTICK1, joystick_payload1)
    mqttc.publish(TOPIC_JOYSTICK2, joystick_payload2)
    mqttc.publish(TOPIC_BUTTONS, buttons_payload)

    time.sleep(5)