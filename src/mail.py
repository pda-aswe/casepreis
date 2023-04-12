import paho.mqtt.publish as publish
import os
import json

class Mail:
    @staticmethod
    def send(address,subject,text):
        docker_container = os.environ.get('DOCKER_CONTAINER', False)
        if docker_container:
            mqtt_address = "broker"
        else:
            mqtt_address = "localhost"

        requestData = {
            "to":address,
            "subject":subject,
            "message":text
        }

        publish.single("mail/send",payload=json.dumps(requestData),hostname=mqtt_address,port=1883)