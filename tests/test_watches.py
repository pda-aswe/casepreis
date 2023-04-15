from unittest.mock import patch, mock_open
from src import watches
import json
import datetime

#create watch object once --> is singelton object
with patch("builtins.open",mock_open(read_data='{"observers":[]}')) as mock_data:
        watchd = watches.Watches()

def test_loadData():
    with patch("builtins.open",mock_open(read_data='{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2023-10-24T08:48:34.685496","mailNotify":true}]}')) as mock_data:
        assert watchd._Watches__loadData() == json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2023-10-24T08:48:34.685496","mailNotify":true}]}')["observers"]

def test_deleteWatch():
    watchd.watches = json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2023-10-24T08:48:34.685496","mailNotify":true}]}')["observers"]
    with patch.object(watchd,"saveWatches"):
        watchd.deleteWatch(1)
    assert watchd.watches == []

def test_addWatch():
        with patch.object(watchd,"saveWatches"):

            date = datetime.datetime.now()+datetime.timedelta(days=+1)

            watchd.watches = []

            watchd.addWatch("AAPL",120,date,True)

            newWatch = watchd.watches[0]

            assert newWatch['symbol'] == "AAPL"
            assert newWatch['maxPrice'] == 120
            assert newWatch['until'] == date.isoformat()
            assert newWatch['mailNotify'] == True

def test_saveWatches():
    date = datetime.datetime.now()+datetime.timedelta(days=+1)

    watchd.watches = json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2019-10-24T08:48:34.685496","mailNotify":true},{"id":2,"symbol":"APPL","maxPrice":120,"until":"'+date.isoformat()+'","mailNotify":true}]}')["observers"]

    with patch("builtins.open",mock_open(read_data='{"observers":[]}')) as mock_data:
        watchd.saveWatches()
        text = ""
        for writeD in mock_data.return_value.write.call_args_list:
            text += writeD[0][0]

        assert text == json.dumps(json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2019-10-24T08:48:34.685496","mailNotify":true},{"id":2,"symbol":"APPL","maxPrice":120,"until":"'+date.isoformat()+'","mailNotify":true}]}'))

def test_getAllWatches():
    date = datetime.datetime.now()+datetime.timedelta(days=+1)

    watchd.watches = json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2019-10-24T08:48:34.685496","mailNotify":true},{"id":2,"symbol":"APPL","maxPrice":120,"until":"'+date.isoformat()+'","mailNotify":true}]}')["observers"]

    with patch.object(watchd,"deleteWatch"):
        assert watchd.getAllWatches() == [{"id":2,"symbol":"APPL","maxPrice":120,"until":date,"mailNotify":True}]

def test_getWatch():

    date = datetime.datetime.now()+datetime.timedelta(days=+1)

    watchd.watches = json.loads('{"observers":[{"id":1,"symbol":"APPL","maxPrice":120,"until":"2019-10-24T08:48:34.685496","mailNotify":true},{"id":2,"symbol":"APPL","maxPrice":120,"until":"'+date.isoformat()+'","mailNotify":true}]}')["observers"]
    
    with patch.object(watchd,"saveWatches"):
        assert watchd.getWatch(1) == {}
        assert watchd.getWatch(2) == {"id":2,"symbol":"APPL","maxPrice":120,"until":date,"mailNotify":True}