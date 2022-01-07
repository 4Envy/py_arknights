import json
import hmac
import uuid
import httpx
import pickle

from pathlib import Path
from hashlib import sha1
from typing import Optional, Union
from pydantic.networks import AnyHttpUrl

headers = {  # all requests public headers, don't change!
    "Content-Type": "application/json",
    "X-Unity-Version": "2017.4.39f1",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; KB2000 Build/RP1A.201005.001)",
    "Connection": "Keep-Alive",
}


appkey = "91240f70c09a08a6bc72af1a5c8d4670".encode()

auth_server = "https://as.hypergryph.com"
game_server = "https://ak-gs-gf.hypergryph.com"


class Arknights:
    """arknights request functions"""

    def __init__(
        self,
        username: str,
        password: str = "",
        access_token: str = "",
        device_id: str = "",
        device_id2: str = "",
        session_dir: Union[str, Path] = Path("session"),
        proxy: Optional[AnyHttpUrl] = None,
    ):
        """init account instance"""
        if not password and not access_token:
            raise ValueError("password or access_token must be set")
        self.username = username
        self.password = password
        self.access_token = access_token
        self.session_dir = Path(session_dir)
        self.device_id = device_id or str(uuid.uuid4()).replace("-", "")
        self.device_id2 = device_id2 or str(uuid.uuid4()).replace("-", "")[:16]
        self.proxy = proxy
        self.http = httpx.Client(
            headers=headers,
            proxies={
                "all://": self.proxy,
            },
        )  # Init httpx
        self.nickname = ""
        self.secret = ""
        self.seqnum = 1
        res = self.http.get(
            "https://ak-conf.hypergryph.com/config/prod/official/Android/version"
        ).json()
        self.res_version = res["resVersion"]
        self.client_version = res["clientVersion"]
        res = self.http.get(
            "https://ak-conf.hypergryph.com/config/prod/official/network_config"
        ).json()
        self.network_version = json.loads(res["content"])["configVer"]

    def postAs(self, cgi, data):
        """Post data to Auth Server"""
        req = self.http.post(auth_server + cgi, json=data, headers=headers)
        return req.json()

    def postGs(self, cgi, data):
        """Post data to Game Server"""
        req = self.http.post(game_server + cgi, json=data, headers=self.getGsHeaders())
        result = req.json()
        self.dumpSession()
        return result

    def login(
        self,
    ) -> Union[bool, tuple[str, str, str, str, str]]:
        """account login"""

        print(f"{self.username} login...")
        self.session_file = self.session_dir.joinpath(f"{self.username}.pickle")
        if self.session_file.exists():
            with self.session_file.open("rb") as f:
                session = pickle.load(f)
            (
                self.device_id,
                self.device_id2,
                self.username,
                self.password,
                self.access_token,
                self.uid,
                self.nickname,
                self.proxy,
                self.secret,
                self.seqnum,
                self.res_version,
                self.client_version,
                self.network_version,
            ) = session
            self.seqnum += 1
            print("load cache success")
            return (
                self.username,
                self.uid,
                self.nickname,
                self.access_token,
                self.secret,
            )
        else:
            if self.access_token:
                print("login with access_token")
                if self.authLogin():
                    pass
                else:
                    print("authLogin failed")
                    self.userLogin()
                    self.authLogin()
            else:
                print("login with username and password")
                self.userLogin()
                self.authLogin()

            self.postAs("/user/info/v1/need_cloud_auth", {"token": self.access_token})
            self.getOnline()

        sign_data = {
            "appId": "1",
            "channelId": "1",
            "deviceId": self.device_id,
            "deviceId2": self.device_id2,
            "deviceId3": "",
            "extension": json.dumps(
                {
                    "uid": self.uid,
                    "access_token": self.access_token,
                }
            ),
            "platform": 1,
            "subChannel": "1",
            "worldId": "1",
        }
        sign = u8auth_genSign(sign_data)
        sign_data["sign"] = sign
        res = self.postAs("/u8/user/v1/getToken", sign_data)
        print("getToken...")
        self.uid = res["uid"]
        self.token = res["token"]

        self.postGs(
            "/u8/pay/getAllProductList",
            {"appId": "1", "channelId": "1", "worldId": 1, "platform": 1},
        )

        data = {
            "networkVersion": self.network_version,
            "uid": self.uid,
            "token": self.token,
            "assetsVersion": self.res_version,
            "clientVersion": self.client_version,
            "platform": 1,
            "deviceId": self.device_id,
            "deviceId2": self.device_id2,
            "deviceId3": "",
        }
        res = self.postGs("/account/login", data)
        print("game login...")
        self.secret: str = res["secret"]

        res = self.postGs("/account/syncData", {"platform": 1})
        if res["result"] != 0:
            print("syncData failed")
            return False
        else:
            print("syncData success")
            self.nickname: str = res["user"]["status"]["nickName"]
            data = {"token": self.access_token}
            data["sign"] = u8auth_genSign(data)
            self.postAs("/online/v1/loginout", data)
            self.dumpSession()
            return (
                self.username,
                self.uid,
                self.nickname,
                self.access_token,
                self.secret,
            )

    def getOnline(self):
        """get online status"""
        data = {"token": self.access_token}
        data["sign"] = u8auth_genSign({"token": self.access_token})
        self.postAs("/online/v1/ping", data)

    def authLogin(self):
        """token verify"""
        data = {"token": self.access_token}
        data["sign"] = u8auth_genSign(data)
        res = self.postAs("/user/auth", data)
        if res.get("statusCode", 0) != 0:
            return False
        else:
            self.uid = res["uid"]
            return True

    def userLogin(self):
        """username and password login"""
        data = {
            "account": self.username,
            "password": self.password,
            "deviceId": self.device_id,
            "platform": 1,
        }
        data["sign"] = u8auth_genSign(data)
        res = self.postAs("/user/login", data)
        try:
            self.access_token: str = res["token"]
        except KeyError:
            print(res)
            exit()

    def getGsHeaders(self):
        """get Game Server headers"""
        self.seqnum += 1
        headers["uid"] = self.uid
        headers["secret"] = self.secret
        headers["seqnum"] = str(self.seqnum)
        return headers

    def dumpSession(self):
        """save session"""
        with self.session_file.open("wb") as f:
            pickle.dump(
                (
                    self.device_id,
                    self.device_id2,
                    self.username,
                    self.password,
                    self.access_token,
                    self.uid,
                    self.nickname,
                    self.proxy,
                    self.secret,
                    self.seqnum,
                    self.res_version,
                    self.client_version,
                    self.network_version,
                ),
                f,
            )

    def close(self):
        """close session"""
        self.http.close()
        self.dumpSession()


def u8auth_genSign(value: Union[str, dict]):
    """u8 auth sign"""
    if isinstance(value, dict):
        value = parseUrls({d: value.get(d) for d in sorted(value.keys())})
    hama_code = hmac.new(appkey, value.encode(), sha1)
    return hama_code.hexdigest().lower()


def parseUrls(urls):
    """urls parse"""
    has_ext = False
    final = ""
    for ext, val in urls.items():
        if not has_ext:
            has_ext = True
        else:
            final += "&"
        final += str(ext) + "=" + str(val)
    return final
