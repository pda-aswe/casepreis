import paho.mqtt.client as mqtt
import os
import json
import stock

class Messenger:
    def __init__(self):
        self.connected = False

        #StockService-Object erstellen
        self.stockService = stock.Stock()

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()
        self.mqttConnection.on_connect = self.__onMQTTconnect
        self.mqttConnection.on_message = self.__onMQTTMessage

        #Definition einer Callback-Funktion für ein spezielles Topic
        self.mqttConnection.message_callback_add("req/price", self.__mailMQTTPricecallback)

    def connect(self):
        if not self.connected:
            try:
                docker_container = os.environ.get('DOCKER_CONTAINER', False)
                if docker_container:
                    mqtt_address = "broker"
                else:
                    mqtt_address = "localhost"
                self.mqttConnection.connect(mqtt_address,1883,60)
            except:
                return False
        self.connected = True
        return True
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self.mqttConnection.disconnect()
        return True

    def __onMQTTconnect(self,client,userdata,flags, rc):
        client.subscribe([("req/price",0)])

    def __onMQTTMessage(self,client, userdata, msg):
        pass

    def __mailMQTTPricecallback(self,client, userdata, msg):
        try:
            stockData = json.loads(str(msg.payload.decode("utf-8")))
        except:
            print("Can't decode message")
            return
        
        reqKeys = ['symbol']

        if not all(key in stockData for key in reqKeys):
            print("not all keys available")
            return

        stockResponseData = self.stockService.getStockPrice(stockData["symbol"])

        if stockResponseData:
            self.mqttConnection.publish("price/current",json.dumps(stockResponseData))

    def foreverLoop(self):
        self.mqttConnection.loop_forever()