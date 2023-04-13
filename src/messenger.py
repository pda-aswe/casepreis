import paho.mqtt.client as mqtt
import json
import watches
import price
import threading
from multiprocessing import Process, Queue
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import os
from datetime import datetime  
from datetime import timedelta 

class Messenger():
    def __init__(self):
        self.connected = False
        self.mailAddress = None

        self.watchd = watches.Watches()

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()
        self.mqttConnection.on_connect = self.__onConnectMQTT
        self.mqttConnection.on_message = self.__onMessageMQTT
        self.mqttConnection.message_callback_add("stt", self.__sttMQTTCallback)
        self.mqttConnection.message_callback_add("pref/mail", self.__preferenceMailMQTTCallback)

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
            self.mqttConnection.loop_start()
        self.connected = True
        return True
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self.mqttConnection.loop_stop()
            self.mqttConnection.disconnect()
        return True
    
    def __onConnectMQTT(self,client,userdata,flags, rc):
        client.subscribe([("pref/mail",0),("stt",0)])

    def __sttMQTTCallback(self,client, userdata, msg):
        try:
            sttData = json.loads(str(msg.payload.decode("utf-8")))
        except:
            print("Can't decode message")
            return(False)

        verbs = ["informieren","überprüfen","schauen"]
        nouns = ["aktie"]
        possibleStocks = ["apple","microsoft","amazon"]

        #check if stt  for this use case
        if intersection(sttData["verbs"],verbs) and intersection(sttData["nouns"],nouns):
            stocks = [value["token"] for value in sttData["tokens"] if value["token"] in possibleStocks]
            #check if stock available
            if stocks:
                #add stock stymbol to watchData
                watchData = {"mailNotify":False,"until":datetime.now() + timedelta(days=7)}
                watchData["symbol"] = price.Price.getStockSymbol(stocks[0])
                
                #add amount to watchData and check for Date
                tmpIdx = -1
                amountIdx = -1
                breakFor = 0
                for val in sttData["tokens"]:
                    tmpIdx += 1
                    #check amount
                    if val["token"] in ["euro","dollar"]:
                        amountIdx = tmpIdx-1
                        breakFor += 1

                    #check and set date
                    if val["token"] == "schauen" and len(sttData["tokens"]) > tmpIdx+2:
                            if sttData["tokens"][tmpIdx+1]["type"] == "NUM" and sttData["tokens"][tmpIdx+2]["type"] == "NUM":
                                if sttData["tokens"][tmpIdx+1]["token"][-1] == ".":
                                    day = int(sttData["tokens"][tmpIdx+1]["token"][:-1])
                                else:
                                    day = int(sttData["tokens"][tmpIdx+1]["token"])
                               
                                if sttData["tokens"][tmpIdx+1]["token"][-1] == ".":
                                    month = int(sttData["tokens"][tmpIdx+2]["token"][:-1])
                                else:
                                    month = int(sttData["tokens"][tmpIdx+2]["token"])

                                watchData["until"] = watchData["until"].replace(month=month, day=day)
                                breakFor += 1

                    if breakFor == 2:
                        break


                if amountIdx != -1:
                    watchData["maxPrice"] = sttData["tokens"][amountIdx]["token"]
                    responseThread = threading.Thread(target=self.mailResponseCheck, args=(watchData,))
                    responseThread.start()
                else:
                    self.mqttConnection.publish("tts","Leider habe ich den Wunschpreis nicht verstanden. Bitte Versuche es erneut.")
            else:
                self.mqttConnection.publish("tts","Leider konnte ich keine Aktie unter diesen Namen finden")


    def __preferenceMailMQTTCallback(self,client, userdata, msg):
        self.mailAddress = str(msg.payload.decode("utf-8"))

    def getMailAddress(self):
        return self.mailAddress
    
    def requestMailAddress(self):
        self.mqttConnection.publish("req/pref/mail")

    def sendTTS(self,text):
        self.mqttConnection.publish("tts",str(text))

    #received default mqtt messages
    def __onMessageMQTT(self,client, userdata, msg):
        pass

    def mailResponseCheck(self,watchData):
        q = Queue()
        process = Process(target=mqttRequestResponseProzess, args=(q,"tts","Sollen zusätzliche Informationen zur Aktie dir per Mail zugeschickt werden?","stt"))
        process.start()
        process.join(timeout=15)
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

            for value in mqttData["tokens"]:
                if value["token"] == "ja":
                    watchData["mailNotify"] = True
                    break

        self.watchd.addWatch(watchData["symbol"],watchData["maxPrice"],watchData["until"],watchData["mailNotify"])
        self.mqttConnection.publish("tts","Ich werde mich um den Aktienpreis für die nächste Zeit informieren und dir mitteilen, wenn der Wunschpreis erreicht wird.")

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3
       
        
def mqttRequestResponseProzess(q,requestTopic,requestData,responseTopic):
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    if docker_container:
        mqtt_address = "broker"
    else:
        mqtt_address = "localhost"

    publish.single(requestTopic,payload=requestData,hostname=mqtt_address,port=1883)
    mqttResponse = subscribe.simple(responseTopic,hostname=mqtt_address,port=1883).payload

    q.put(mqttResponse)