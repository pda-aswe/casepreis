from src import mail
from unittest.mock import patch, ANY, MagicMock
import json

@patch("paho.mqtt.publish.single")
def test_send(mock_publish):
    requestData = {
        "to":"Adresse",
        "subject":"Betreff",
        "message":["Text"]
    }

    mail.Mail.send("Adresse","Betreff",["Text"])

    mock_publish.assert_called_with("mail/send",payload=json.dumps(requestData),hostname=ANY,port=ANY)