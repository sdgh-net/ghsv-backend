import time
from DBUtil import db
from FlaskError import SupervisionExistError
from User import User
import Idea  # 这里有循环引用，可能需要修改


class Supervision:
    sid: int | None = None

    def __init__(self, sid: int | None):
        assert (type(sid) is not str)
        self.sid = sid

    @classmethod
    def clearAllIdeas(cls):
        db.exec("DELETE from idea")

    @classmethod
    def clearAllSupervision(cls):
        db.exec("DELETE from supervision")
        cls.clearAllIdeas()

    def delete(self):
        db.exec("DELETE from supervision where sid=?", (self.sid,))
        db.exec("DELETE from idea where sid=?", (self.sid,))

    @classmethod
    def new(cls, name: str, until: int, target_group: str, error_on_exist: bool = True):
        if cls.getSupervisionByName(name) is not None:
            if not error_on_exist:
                return cls.getSupervisionByName(name)
            raise SupervisionExistError(name)
        db.exec(
            "INSERT INTO supervision (name, until, target_group) VALUES(?,?,?)", (name, until, target_group))
        u = Supervision.getSupervisionByName(name)
        return u

    @classmethod
    def getSupervisionByName(cls, name: str):
        res = [i[0] for i in db.exec(
            "select sid from supervision where name=?", (name,)).fetchall()]
        if len(res) == 0:
            return None
        assert (len(res) == 1)
        return cls(res[0])

    def getSid(self) -> int | None:
        return self.sid

    def switchToSid(self, sid: int | None):
        """
        改变当前对象的 sid，而不修改数据库
        """
        self.sid = sid

    def getGroups(self) -> set:
        return set(db.exec("select target_group from supervision where sid=?", (self.sid,)).fetchall()[0][0].split(','))

    def shouldShowForGroup(self, group: str):
        return group in self.getGroups()

    def shouldShowForUser(self, user: User):
        return len(user.getGroups() & self.getGroups()) >= 1

    def setGroup(self, group: str):
        db.exec("update supervision set target_group = ? where sid=?",
                (group, self.sid))

    def getUntil(self) -> int:
        """
        返回截止时间，以秒为单位的 int 值
        """
        return db.exec("select until from supervision where sid=?", (self.sid,)).fetchall()[0][0]

    def isExpired(self) -> bool:
        if self.getUntil() == -1:  # 以 -1 标记长期有效
            return False
        return int(time.time()) >= self.getUntil()

    def setUntil(self, until: int):
        """
        设置截止时间，以秒为单位的 int 值
        """
        db.exec("update supervision set until = ? where sid=?",
                (until, self.sid))

    def getName(self) -> str:
        return db.exec("select name from supervision where sid=?", (self.sid,)).fetchall()[0][0]

    def setName(self, name: str):
        db.exec("update supervision set name = ? where sid=?",
                (name, self.sid))

    @classmethod
    def listSupervision(cls) -> list:
        """
        获取所有监督，返回 Supervision 对象列表
        """
        return [cls(i[0]) for i in db.exec("select sid from supervision").fetchall()]

    def listIdeas(self) -> list:
        """
        获取所有下属意见，返回 Idea 对象列表
        """
        return [Idea.Idea(i[0]) for i in db.exec("select iid from idea where sid=?", (self.sid,)).fetchall()]

    @classmethod
    def listAllIdeas(cls) -> list:
        """
        获取所有意见，返回 Idea 对象列表
        """
        return [Idea.Idea(i[0]) for i in db.exec("select iid from idea").fetchall()]

    def toDict(self) -> dict:
        return {"sid": self.getSid(),
                "name": self.getName(),
                "until": self.getUntil(),
                "target_group": self.getGroups(),
                }

    def toAPI(self) -> dict:
        dic = self.toDict()
        dic["target_group"] = list(dic["target_group"])
        return dic

    def isSupervisionExist(self):
        if self.sid is None:
            return False
        return len(db.exec("select 1 from supervision where sid=?", (self.sid,)).fetchall()) == 1

    def getStatistic(self) -> dict:
        ideas = self.listIdeas()
        unprocessed = [i for i in ideas if i.getStatus() ==
                       Idea.Idea.Const.IDEA_UNPROCESSED]
        accepted = [i for i in ideas if i.getStatus() ==
                    Idea.Idea.Const.IDEA_ACCEPTED]
        declined = [i for i in ideas if i.getStatus() ==
                    Idea.Idea.Const.IDEA_REJECTED]
        return {"total": len(ideas), "unprocessed": len(unprocessed), "accepted": len(accepted), "declined": len(declined)}

    @classmethod
    def getOverallStatistic(cls) -> dict:
        ideas = cls.listAllIdeas()
        unprocessed = [i for i in ideas if i.getStatus() ==
                       Idea.Idea.Const.IDEA_UNPROCESSED]
        accepted = [i for i in ideas if i.getStatus() ==
                    Idea.Idea.Const.IDEA_ACCEPTED]
        declined = [i for i in ideas if i.getStatus() ==
                    Idea.Idea.Const.IDEA_REJECTED]
        return {"total": len(ideas), "unprocessed": len(unprocessed), "accepted": len(accepted), "declined": len(declined)}

    def exportToJson(self) -> dict:
        res = self.toAPI()
        ideas = []
        for i in self.listIdeas():
            ideas.append(i.toAPI())
        res["ideas"] = ideas
        return res

#print(Supervision.new("test", -1, "gy").getSid())
