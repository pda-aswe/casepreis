from src import price
from unittest.mock import patch, ANY, MagicMock
from multiprocessing import Queue
import json

def test_getStockSymbol():
    assert price.Price.getStockSymbol("apple") == "AAPL"
    assert price.Price.getStockSymbol("asdf") is None

def test_getStockName():
    assert price.Price.getStockName("aapl") == "Apple"
    assert price.Price.getStockName("asdf") is None

@patch("paho.mqtt.publish.single")
@patch("paho.mqtt.subscribe.simple")
def test_mqttRequestResponseProzess(mock_sub,mock_pub):
    mock_sub.return_value = type('obj', (object,), {'payload' : 'asdf'})
    q = Queue()
    price.Price.mqttRequestResponseProzess(q,"test/request",{"symbol":"AAPL"},"test/response")
    mock_pub.assert_called_with("test/request",payload=json.dumps({"symbol":"AAPL"}),hostname=ANY,port=ANY)
    mock_sub.assert_called_with("test/response",hostname=ANY,port=ANY)
