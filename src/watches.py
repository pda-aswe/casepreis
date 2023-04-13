import json
import time
import datetime

import singelton
class Watches(metaclass=singelton.SingletonMeta):
    def __init__(self):
        self.watches = self.__loadData()

    def __loadData(self):
        try:
            with open('watches.json') as watchesFile:
                return json.load(watchesFile).get("observers",[])
        except:
            return []
    
    def deleteWatch(self,id):
        for watch in self.watches:
            if watch['id'] == id:
                self.watches.remove(watch)
                self.saveWatches()
                break

    def saveWatches(self):
        outputData = {"observers":self.watches}

        with open("watches.json", "w") as outfile:
            json.dump(outputData, outfile)

    def addWatch(self,symbol,maxPrice,until,mailNotify):
        watch = {
            "id":int(time.time()),
            "symbol":symbol,
            "maxPrice":maxPrice,
            "until":until.isoformat(),
            "mailNotify":mailNotify
        }
        self.watches.append(watch)
        self.saveWatches()

    def getAllWatches(self):
        returnData = []
        for watch in self.watches:
            localWatch = watch.copy()
            if datetime.datetime.now() < datetime.datetime.fromisoformat(localWatch['until']): 
                localWatch["until"] = datetime.datetime.fromisoformat(localWatch['until'])
                returnData.append(localWatch)
            else:
                self.deleteWatch(localWatch['id'])
        
        return returnData

    def getWatch(self,id):
        for watch in self.watches:
            localWatch = watch.copy()
            if localWatch['id'] == id:
                if datetime.datetime.now() < datetime.datetime.fromisoformat(localWatch['until']): 
                    localWatch["until"] = datetime.datetime.fromisoformat(localWatch['until'])
                    return localWatch
                else:
                    self.deleteWatch(localWatch['id'])
                    return {}
            
        return {}