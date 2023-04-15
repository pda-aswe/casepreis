from unittest.mock import patch, mock_open
from src import watches
import json
import datetime

def test_loadData():
    with patch("builtins.open",mock_open(read_data='{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2023-10-24T08:48:34.685496","mailNotify":true}]}')) as mock_data:
        obj = watches.Watches()
        assert obj._Watches__loadData() == json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2023-10-24T08:48:34.685496","mailNotify":true}]}')["observers"]

    del obj

def test_deleteWatch():
    with patch("builtins.open",mock_open(read_data='{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2023-10-24T08:48:34.685496","mailNotify":true}]}')) as mock_data:
        obj = watches.Watches()
        obj.deleteWatch(1)
        assert obj.watches == []

    del obj

def test_addWatch():
    obj = watches.Watches()

    with patch("builtins.open",mock_open(read_data='{"observers":[]}')) as mock_data, patch.object(obj,"saveWatches"):

        date = datetime.datetime.now()+datetime.timedelta(days=+1)

        obj.addWatch("AAPL",120,date,True)

        newWatch = obj.watches[0]

        assert newWatch['symbol'] == "AAPL"
        assert newWatch['maxPrice'] == 120
        assert newWatch['until'] == date.isoformat()
        assert newWatch['mailNotify'] == True

    del obj

def test_saveWatches():
    pass

def test_getAllWatches():
    pass

"""def test_getWatch():

    date = datetime.datetime.now()+datetime.timedelta(days=+1)

    fileData = '{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2019-10-24T08:48:34.685496","mailNotify":true},{"id":2,"symbol":"APPL","maxPrice":120,"until":"'+date.isoformat()+'","mailNotify":true}]}'

    with patch("builtins.open",mock_open(read_data=fileData)) as mock_data:
        obj = watches.Watches()
        
        print(obj.watches)

        assert False

    del obj"""