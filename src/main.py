#!/usr/bin/python3
import time

#own libraries
import messenger
import price
import mail

if __name__ ==  "__main__":
    #setup mqtt client
    mqttConnection = messenger.Messenger()
    if not mqttConnection.connect():
        print("No MQTT broker running")
        quit()

    #dict of pice watchData
    observerData = {
        "observers":[
        {
        "id":0,
        "maxPrice":23.00,
        "until":"2023-04-20T22:00:00+02:00",
        "symbol":"AAPL",
        "mailNotify":True}
        ]
    }

    #get preference mail address
    mqttConnection.requestMailAddress()


    print(price.Price.getStockSymbol("apple"))
    #mail.Mail.send("fabiankuffer@live.de","Testmail",["Zeile 1","Zeile 2"])

    while True:
        print(price.Price.currentPrice("req/price",{"symbol":"AAPL"},"price/current"))
        time.sleep(60)

    #stop mqtt
    mqttConnection.disconnect()