import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
from multiprocessing import Process, Queue
import json
import os

class Price:
    @staticmethod
    def currentPrice(requestTopic,requestData,responseTopic):
        q = Queue()
        process = Process(target=Price.mqttRequestResponseProzess, args=(q,requestTopic,requestData,responseTopic))
        process.start()
        process.join(timeout=3)
        process.terminate()
        if process.exitcode == 0:
            try:
                mqttData = q.get(timeout=1)
            except:
                return(False)

            try:
                mqttData = json.loads(str(mqttData.decode("utf-8")))
            except:
                print("Can't decode message")
                return(False)

            return mqttData
        else:
            return {}

    @staticmethod
    def mqttRequestResponseProzess(q,requestTopic,requestData,responseTopic):
        docker_container = os.environ.get('DOCKER_CONTAINER', False)
        if docker_container:
            mqtt_address = "broker"
        else:
            mqtt_address = "localhost"

        publish.single(requestTopic,payload=json.dumps(requestData),hostname=mqtt_address,port=1883)
        mqttResponse = subscribe.simple(responseTopic,hostname=mqtt_address,port=1883).payload

        q.put(mqttResponse)

    @staticmethod
    def getStockSymbol(companyName):
        companyName = companyName.lower()
        stockSymbols = {
            "apple":"AAPL",
            "microsoft":"MSFT",
            "amazon":"AMZN"
        }
        return stockSymbols.get(companyName,None)