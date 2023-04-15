from src import messenger
from unittest.mock import patch, ANY, MagicMock
from multiprocessing import Queue
import json

class DummyMSG:
    def __init__(self):
        self.payload = "Test"
        self.topic = "test"

    def set_payload(self,data):
        self.payload = str.encode(data)

    def set_topic(self,topic):
        self.topic = topic

@patch("watches.Watches")
def test_connect(mock_watchd):
    obj = messenger.Messenger()

    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.connect()
        mock_connect.connect.assert_called_with("localhost",1883,60)
        mock_connect.loop_start.assert_called()

@patch("watches.Watches")
def test_disconnect(mock_watchd):
    obj = messenger.Messenger()

    with patch.object(obj, 'connected', True), patch.object(obj, 'mqttConnection') as mock_connect:
        obj.disconnect()
        mock_connect.disconnect.assert_called()
        mock_connect.loop_stop.assert_called()

@patch("watches.Watches")
def test_onConnectMQTT(mock_watchd):
    obj = messenger.Messenger()

    mock_client = MagicMock()

    obj._Messenger__onConnectMQTT(mock_client,None,None,None)

    mock_client.subscribe.assert_called_with([("pref/mail",0),("stt",0)])


@patch("watches.Watches")
def test_onMessageMQTT(mock_watchd):
    obj = messenger.Messenger()

    obj._Messenger__onMessageMQTT(MagicMock(),None,None)

def test_intersection():
    assert messenger.intersection(["asdf","1234"],["jklö"]) == []
    assert messenger.intersection(["asdf","1234"],["asdf"]) == ["asdf"]

@patch("paho.mqtt.publish.single")
@patch("paho.mqtt.subscribe.simple")
def test_mqttRequestResponseProzess(mock_sub,mock_pub):
    mock_sub.return_value = type('obj', (object,), {'payload' : 'asdf'})
    q = Queue()
    messenger.mqttRequestResponseProzess(q,"test/request","asdf","test/response")
    mock_pub.assert_called_with("test/request",payload="asdf",hostname=ANY,port=ANY)
    mock_sub.assert_called_with("test/response",hostname=ANY,port=ANY)

@patch("watches.Watches")
def test_sendTTS(mock_watchd):
    obj = messenger.Messenger()

    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.sendTTS("testMessage")
        mock_connect.publish.assert_called_with("tts","testMessage")

@patch("watches.Watches")
def test_requestMailAddress(mock_watchd):
    obj = messenger.Messenger()

    with patch.object(obj, 'mqttConnection') as mock_connect:
        obj.requestMailAddress()
        mock_connect.publish.assert_called_with("req/pref/mail")

@patch("watches.Watches")
def test_preferenceMailMQTTCallback(mock_watchd):
    obj = messenger.Messenger()

    responseData = DummyMSG()
    responseData.set_payload("testMailAddress")

    obj._Messenger__preferenceMailMQTTCallback(None,None,responseData)

    assert obj.mailAddress == "testMailAddress"

@patch("watches.Watches")
def test_getMailAddress(mock_watchd):
    obj = messenger.Messenger()
    assert obj.getMailAddress() is None

    obj.mailAddress = "testMailAddress"
    assert obj.getMailAddress() == "testMailAddress"
