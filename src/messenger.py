import paho.mqtt.client as mqtt

class Messenger():
    def __init__(self):
        self.connected = False
        self.mailAddress = None

        #aufbau der MQTT-Verbindung
        self.mqttConnection = mqtt.Client()
        self.mqttConnection.on_connect = self.__onConnectMQTT
        self.mqttConnection.on_message = self.__onMessageMQTT
        self.mqttConnection.message_callback_add("stt", self.__sttMQTTCallback)
        self.mqttConnection.message_callback_add("pref/mail", self.__preferenceMailMQTTCallback)

    def connect(self):
        if not self.connected:
            try:
                self.mqttConnection.connect("localhost",1883,60)
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
        pass

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