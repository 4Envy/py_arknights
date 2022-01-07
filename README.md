# Py Arknights
arknights CN request functions

### Install
```shell
pip install arknights
```

### Usage
```python
from pathlib import Path
from arknights import Arknights

ark = Arknights(
    "18888888888",                        # phone number
    "xxxxxxx",                            # password
    "",                                   # access_token (if you have
    "ffffffffffffffffffffffffffffffff",   # device_id
    "ffffffffffffffff",                   # device_id2
    Path("accs"),                         # session_dir
    "http://127.0.0.1:1080"               # http proxy
)

print(ark.login())

id_range = [str(x) for x in range(1, 10)]
players_list = acc1.postGs("/social/searchPlayer", {"idList": id_range})

print(players_list)
```
