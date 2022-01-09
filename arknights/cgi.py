from . import Arknights


class AkCall:
    class Account:
        def __init__(self, ak: Arknights):
            self.ak = ak

        @classmethod
        def syncData(self) -> dict:
            """
            sync player data

            同步玩家数据
            """
            return self.ak.postGs("/account/syncData", {"platform": 1})

    class Social:
        def __init__(self, ak: Arknights):
            self.ak = ak

        @classmethod
        def searchPlayer(self, idList: list[str]) -> dict:
            """
            search player info by idList

            通过 id 列表查寻玩家详细信息
            """
            return self.ak.postGs("/social/searchPlayer", {"idList": idList})

        @classmethod
        def getSortListInfo(self, nickname: str, nicknumber: str = "") -> dict:
            """
            get sorted player list by nickname and nicknumber

            通过昵称和编号获取已排序的玩家列表
            """
            return self.ak.postToGs(
                "/social/getSortListInfo",
                {
                    "type": 0,
                    "sortKeyList": ["level"],
                    "param": {"nickName": nickname, "nickNumber": nicknumber},
                },
            )

        @classmethod
        def getFriendList(self, idList: list[str]) -> dict:
            """
            get friend list

            获取好友列表
            """
            return self.ak.postGs("/social/getFriendList", {"idList": idList})
