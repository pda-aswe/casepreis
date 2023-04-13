#!/usr/bin/python3
import time

#own libraries
import messenger
import price
import mail
import watches
import datetime

if __name__ ==  "__main__":
    #setup mqtt client
    mqttConnection = messenger.Messenger()
    if not mqttConnection.connect():
        print("No MQTT broker running")
        quit()

    #load all stock watches
    watchStore = watches.Watches()

    #get preference mail address
    if not mqttConnection.getMailAddress:
        mqttConnection.requestMailAddress()


    #check stock prices forever
    while True:
        time.sleep(30)
        stockData = {}
        for watch in watchStore.getAllWatches():
            if watch["symbol"] not in stockData:
                stockData[watch["symbol"]] = price.Price.currentPrice("req/price",{"symbol":watch["symbol"]},"price/current")
            
            if stockData[watch["symbol"]]["current"] < watch["maxPrice"]:
                ttsMessage = "Für die Aktie "+price.Price.getStockName(watch["symbol"])+" wurde der Wunschpreis erreicht."
                if watch["mailNotify"] and mqttConnection.getMailAddress():
                    mail.Mail.send(mqttConnection.getMailAddress(),"Aktienwunschpreis",["Aktiensymbol: "+watch["symbol"],"Aktueller Preis: "+str(round(stockData[watch["symbol"]]["current"],2))+"$","Tageshöchstpreis: "+str(round(stockData[watch["symbol"]]["highestDay"],2))+"$","Niedrigster Tagespreis: "+str(round(stockData[watch["symbol"]]["lowestDay"],2))+"$"])
                    ttsMessage += " Weitere Informationen habe ich dir per Mail zugesendet."
                mqttConnection.sendTTS(ttsMessage)
                watchStore.deleteWatch(watch["id"])

    #stop mqtt
    mqttConnection.disconnect()