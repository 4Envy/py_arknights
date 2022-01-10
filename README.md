# Py Arknights

arknights CN request functions

### Install

```shell
pip install arknights
```

### Usage

```python
from pathlib import Path
from arknights import Arknights, AkCall

ark = Arknights(
    username="18888888888",                         # phone number
    password="xxxxxxx",                             # password
    access_token="",                                # access_token (if you have
    device_id="ffffffffffffffffffffffffffffffff",   # device_id
    device_id2="ffffffffffffffff",                  # device_id2
    relogin=True,                                   # auto relogin
    session_dir=Path("accs"),                       # session_dir
    proxy="http://127.0.0.1:1080"                   # http proxy
)

ark.login()


AkCall(ark).Account.syncData()

search_player = AkCall(ark).Social.getSortListInfo("两面包夹芝士", "")
player_list = AkCall(ark).Social.searchPlayer(
    [x["uid"] for x in search_player["result"]]
)

for player in player_list["result"]:
    nickName = player["nickName"]
    print(nickName)
```
