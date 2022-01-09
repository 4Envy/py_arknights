from .ak import Arknights


class AkCall:
    class Account:
        def __init__(self, acc: Arknights):
            self.acc = acc

        def syncData(self) -> dict:
            """
            sync player data

            同步玩家数据
            """
            return self.acc.postGs("/account/syncData", {"platform": 1})

    class Social:
        def __init__(self, acc: Arknights):
            self.acc = acc

        def getFriendList(self, idList: list[str]) -> dict:
            """
            get player detail info by idList

            通过 idList 获取玩家详细信息
            """
            return self.acc.postGs("/social/getFriendList", {"idList": idList})

        def getSortListInfo(
            self,
            nickname: str,
            nicknumber: str = "",
            sort: bool = False,
            sortkey: str = "level",
        ) -> dict:
            """
            get sorted player list by nickname and nicknumber,can sort by level or uid

            通过昵称和编号获取玩家列表，可选择是否按照等级"level"或"uid"排序
            """
            result = self.acc.postGs(
                "/social/getSortListInfo",
                {
                    "type": 0,
                    "sortKeyList": ["level"],
                    "param": {"nickName": nickname, "nickNumber": nicknumber},
                },
            )
            if sort:
                if sortkey == "level":
                    result["result"].sort(
                        key=lambda k: (k.get("level", 0), int(k.get("uid", 0))),
                        reverse=True,
                    )
                elif sortkey == "uid":
                    result["result"].sort(
                        key=lambda k: (int(k.get("uid", 0))), reverse=True
                    )
                else:
                    raise ValueError("sortkey must be level or uid")
            return result

        def searchPlayer(self, idList: list[str]) -> dict:
            """
            search player info by idList

            通过 id 列表查寻玩家详细信息
            """
            return self.acc.postGs("/social/searchPlayer", {"idList": idList})
