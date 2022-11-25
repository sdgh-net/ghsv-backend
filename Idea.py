from random import randint
import time
from DBUtil import db
import Supervision
import User
import json


class Idea:
    class Const:
        IDEA_UNPROCESSED = 0
        IDEA_ACCEPTED = 1
        IDEA_REJECTED = 2
        IDEA_DUPLICATED = 3
        IDEA_TRASH = 4
        IDEA_DELETED = 5
        ALL_IDEA_STATUS = [IDEA_UNPROCESSED, IDEA_ACCEPTED,
                           IDEA_REJECTED, IDEA_DUPLICATED, IDEA_TRASH, IDEA_DELETED]
    iid: int | None = None

    def __init__(self, iid: int | None):
        assert (type(iid) is not str)
        self.iid = iid

    @classmethod
    def clearAllIdeas(cls):
        db.exec("DELETE from idea")

    def delete(self):
        db.exec("DELETE from idea where iid=?", (self.iid,))

    @classmethod
    def getLatestIid(cls):
        r = db.exec("select iid from idea order by iid desc limit 1").fetchall()
        if len(r) == 0:
            return 0  # AUTOINCREMENT 由 1 开始
        return r[0][0]

    @classmethod
    def new(cls, proponent: int, target: int, content: str, sid: int, time: int, status: int = 0):
        iid = cls.getLatestIid()+1
        db.exec(
            "INSERT INTO idea (iid,proponent, target, content, sid, status, time) VALUES(?,?,?,?,?,?,?)", (iid, proponent, target, content, sid, status, time))
        u = Idea(iid)
        return u

    def getIid(self) -> int | None:
        return self.iid

    def switchToIid(self, iid: int | None):
        """
        改变当前对象的 iid，而不修改数据库
        """
        self.iid = iid

    def getSid(self) -> int:
        return db.exec("select sid from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setSid(self, sid: int):
        db.exec("update idea set sid = ? where iid=?",
                (sid, self.iid))

    def getProponent(self) -> int:
        return db.exec("select proponent from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setProponent(self, proponent: int):
        db.exec("update idea set proponent = ? where iid=?",
                (proponent, self.iid))

    def getProponentUser(self) -> User.User:
        return User.User(self.getProponent())

    def getProponentUserNickname(self) -> str | None:
        u = self.getProponentUser()
        if u is None or not u.isUserExist():
            return None
        return u.getNickname()

    def setProponentUser(self, proponent_user: User.User):
        self.setProponent(proponent_user.getUid())  # type: ignore

    def getStatus(self) -> int:
        return db.exec("select status from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setStatus(self, status: int):
        db.exec("update idea set status = ? where iid=?",
                (status, self.iid))

    def getTime(self) -> int:
        return db.exec("select time from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setTime(self, time: int):
        db.exec("update idea set time = ? where iid=?",
                (time, self.iid))

    def getExtra(self) -> dict:
        return json.loads(self.getRawExtra())

    def setExtra(self, extra: dict):
        self.setRawExtra(json.dumps(extra))

    def getRawExtra(self):
        return db.exec("select extra from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setRawExtra(self, extra: str):
        db.exec("update idea set extra = ? where iid=?",
                (extra, self.iid))

    def getTarget(self) -> int:
        return db.exec("select target from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setTarget(self, target: int):
        db.exec("update idea set target = ? where iid=?",
                (target, self.iid))

    def getTargetUser(self) -> User.User:
        return User.User(self.getTarget())

    def setTargetUser(self, target_user: User.User):
        self.setTarget(target_user.getUid())  # type: ignore

    def getTargetUserNickname(self) -> str | None:
        u = self.getTargetUser()
        if u is None or not u.isUserExist():
            return None
        return u.getNickname()

    def getContent(self) -> str:
        return db.exec("select content from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setContent(self, content: str):
        db.exec("update idea set content = ? where iid=?",
                (content, self.iid))

    def getReply(self) -> str | None:
        return db.exec("select reply from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setReply(self, reply: str | None):
        db.exec("update idea set reply = ? where iid=?",
                (reply, self.iid))

    def getDuplicate(self) -> int | None:
        raise NotImplementedError  # 均已经没必要搞了
        return db.exec("select reply from idea where iid=?", (self.iid,)).fetchall()[0][0]

    def setDuplicate(self, duplicate: int | None):
        raise NotImplementedError
        db.exec("update idea set duplicate = ? where iid=?",
                (duplicate, self.iid))

    def getSupervision(self):
        return Supervision.Supervision(self.getSid())

    @classmethod
    def listIdea(cls, sid: int | None = None, status: int | None = None, proponent: int | None = None, target: int | None = None) -> list:
        """
        获取所有意见，返回 Idea 对象列表
        """
        res = [cls(i[0]) for i in db.exec("select iid from idea").fetchall()]
        if sid is not None:
            res = [i for i in res if i.getSid() == sid]
        if status is not None:
            res = [i for i in res if i.getStatus() == status]
        if proponent is not None:
            res = [i for i in res if i.getProponent() == proponent]
        if target is not None:
            res = [i for i in res if i.getTarget() == target]
        return res

    def toDict(self) -> dict:
        return {"iid": self.getIid(),
                "sid": self.getSid(),
                "proponent": self.getProponent(),
                "target": self.getTarget(),
                "content": self.getContent(),
                "status": self.getStatus(),
                "time": self.getTime(),
                "extra": self.getExtra(),
                "reply": self.getReply(),
                }

    def toPrettyStr(self) -> str:
        """
        用于生成在导出的 docx 文件中显示的内容
        """
        stat = self.getStatus()
        stat_str: str = ""
        if stat == self.Const.IDEA_UNPROCESSED:
            stat_str = "未处理"
        elif stat == self.Const.IDEA_ACCEPTED:
            stat_str = "√"
        elif stat == self.Const.IDEA_REJECTED:
            stat_str = "×"
        else:
            raise ValueError(f"意见状态 {stat} 错误")
        stat_str = f"[{stat_str}]"
        reply = self.getReply()
        if reply is None:
            return stat_str
        return stat_str + " " + reply

    def toAPI(self) -> dict:
        dic = self.toDict()
        dic["proponent_user_nickname"] = self.getProponentUserNickname()
        dic["target_user_nickname"] = self.getTargetUserNickname()
        return dic

    def isIdeaExist(self):
        if self.iid is None:
            return False
        return len(db.exec("select 1 from idea where iid=?", (self.iid,)).fetchall()) == 1

