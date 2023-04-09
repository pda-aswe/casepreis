import finnhub
import datetime
import json
import os

class Stock:
    def __init__(self):
        self.apiKey = self.__loadAPIKey()
        self.finnhub_client = finnhub.Client(api_key=self.apiKey)

    def __loadAPIKey(self):
        if os.path.exists('key.txt'):
            with open('key.txt') as f:
                return f.readline().strip('\n')
        else:
            print("api key file missing")
            quit()

    def getStockPrice(self,symbol):
        returnData = {}
        try:
            stockData = self.finnhub_client.quote(symbol)
        except Exception as e:
            stockData = {}

        if stockData:
            if stockData["t"] > 0:
                returnData["symbol"] = symbol
                returnData["current"] = stockData['c']
                returnData["highestDay"] = stockData['h']
                returnData["lowestDay"] = stockData['l']
                returnData["timestamp"] = stockData['t']

        return returnData