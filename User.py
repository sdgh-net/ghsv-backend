import functools
import json
from Config import Config
from DBUtil import db
from werkzeug.security import generate_password_hash, check_password_hash
import flask_login
from Functions import sha256
import time
import MailUtil
from FlaskError import GroupIdExistError, GroupIdNonExistError, PasswordWrongTooMuchError, PermissionDeniedError, UserExistError, UserIdNonExistError, UserNonExistError
import urllib


def init_login_manager(login_manager):
    @login_manager.user_loader
    def user_loader(uid_str):
        u = User.getUserByFlaskId(uid_str)
        if u is None or (not u.isUserExist()):
            return None
        return u


class User(flask_login.UserMixin):
    uid: int | None = None

    @classmethod
    def clearAllUsers(cls):
        db.exec("DELETE from user")

    @classmethod
    def clearAllLoginAttempts(cls):
        db.exec("DELETE from login_attempt")

    @classmethod
    def new(cls, username: str, nickname: str, password: str, power: str, user_group: str, email: str | None = None, error_on_exist: bool = True):
        if cls.getUserByUsername(username) is not None:
            if not error_on_exist:
                return User.getUserByUsername(username)
            raise UserExistError(username)
        password = generate_password_hash(password)
        db.exec(
            "INSERT INTO user (username, nickname, password, power, user_group, email, flask_id) VALUES(?,?,?,?,?,?,'null')", (username, nickname, password, power, user_group, email))
        u = User.getUserByUsername(username)
        if u is not None:
            u.updateFlaskId()
        return u

    def deleteLoginAttempts(self):
        db.exec(
            "DELETE from login_attempt where uid=?", (self.uid))

    def delete(self, error_on_non_exist: bool = True):
        if not self.isUserExist():
            if not error_on_non_exist:
                return
            raise UserIdNonExistError(self.uid)
        db.exec(
            "DELETE from user where uid=?", (self.uid))

    @classmethod
    def getUserByUsername(cls, username: str):
        res = [i[0] for i in db.exec(
            "select uid from user where username=?", (username,)).fetchall()]
        if len(res) == 0:
            return None
        assert (len(res) == 1)
        return cls(res[0])

    @classmethod
    def getUsersByGroup(cls, group: str) -> list:
        res = [i[0] for i in db.exec(
            "select uid from user where user_group=?", (group,)).fetchall()]
        return [cls(i) for i in res]

    @classmethod
    def getGroupName(cls, group_id: str) -> str | None:
        res = [i[0] for i in db.exec(
            "select group_name from user_group where group_id=?", (group_id,)).fetchall()]
        if len(res) == 0:
            return None
        assert (len(res) == 1)
        return res[0]

    @classmethod
    def newGroup(cls, group_id: str, group_name: str, power: str):
        if cls.getGroupName(group_id) is not None:
            raise GroupIdExistError(group_id)
        db.exec(
            "INSERT INTO user_group (group_id, group_name, power) VALUES(?,?,?)", (group_id, group_name, power))

    @classmethod
    def changeGroupName(cls, group_id: str, group_name: str):
        if cls.getGroupName(group_id) is None:
            raise GroupIdNonExistError(group_id)
        db.exec(
            "UPDATE user_group set group_name = ? where group_id = ?",  group_name, group_id)

    @classmethod
    def changeGroupPower(cls, group_id: str, power: str):
        if cls.getGroupName(group_id) is None:
            raise GroupIdNonExistError(group_id)
        db.exec(
            "UPDATE user_group set power = ? where group_id = ?",  power, group_id)

    @ classmethod
    def getUserByFlaskId(cls, flask_id: str):
        res=[i[0] for i in db.exec(
            "select uid from user where flask_id=?", (flask_id,)).fetchall()]
        if len(res) == 0:
            return None
        assert (len(res) == 1)
        return cls(res[0])

    def __init__(self, uid: int | None):
        assert (type(uid) is not str)
        self.uid=uid

    def __repr__(self) -> str:
        return f"User(uid={self.uid}, username={self.getUsername()}, nickname={self.getNickname()})"

    @ classmethod
    def listUser(cls) -> list:
        """
        获取所有用户，返回 User 对象列表
        """
        return [cls(i[0]) for i in db.exec("select uid from user").fetchall()]

    @ classmethod
    def listApartments(cls) -> list:
        """
        获取所有部门，返回 User 对象列表
        """
        return [i for i in cls.listUser() if i.isInGroup("apartment")]

    def toDict(self) -> dict:
        return {"uid": self.getUid(),
                "username": self.getUsername(),
                "nickname": self.getNickname(),
                "password": self.getPassword(),
                "power": self.getPowers(),
                "user_group": self.getGroups(),
                "last_login_ip": self.getLastLoginIP(),
                "email": self.getEmail(),
                "preferences": self.getPreferences(), }

    def toAPI(self) -> dict:
        dic = self.toDict()
        dic.pop("password")
        dic.pop("preferences")
        dic["power"] = list(dic["power"])
        dic["user_group"] = list(dic["user_group"])
        return dic

    def isUserExist(self):
        if self.uid is None:
            return False
        return len(db.exec("select 1 from user where uid=?", (self.uid,)).fetchall()) == 1

    def getUid(self) -> int | None:
        return self.uid

    def switchToUid(self, uid: int | None):
        """
        改变当前对象的 uid，而不修改数据库
        """
        self.uid = uid

    def getPassword(self) -> str:
        return db.exec("select password from user where uid=?", (self.uid,)).fetchall()[0][0]

    def setPassword(self, password: str):
        password = generate_password_hash(password)
        db.exec("update user set password = ? where uid=?", (password, self.uid))
        self.updateFlaskId()

    def verifyPassword(self, password: str):
        """
        判断给定密码是否正确，正确返回 True
        """
        password_hash = self.getPassword()
        return check_password_hash(password_hash, password)

    def getUsername(self) -> str:
        return db.exec("select username from user where uid=?", (self.uid,)).fetchall()[0][0]

    def setUsername(self, username: str):
        db.exec("update user set username = ? where uid=?", (username, self.uid))
        self.updateFlaskId()

    def getNickname(self) -> str:
        return db.exec("select nickname from user where uid=?", (self.uid,)).fetchall()[0][0]

    def setNickname(self, nickname: str):
        db.exec("update user set nickname = ? where uid=?", (nickname, self.uid))

    def getPowers(self) -> set[str]:
        return set(db.exec("select power from user where uid=?", (self.uid,)).fetchall()[0][0].split(','))

    def addPower(self, new_power: str):
        current_power = self.getPowers()
        new_power = current_power | {new_power}  # type: ignore
        self.setPower(','.join(new_power))

    def removePower(self, remove_power: str):
        current_power = self.getPowers()
        new_power = current_power - {remove_power}  # type: ignore
        self.setPower(','.join(new_power))

    def hasPower(self, power: str) -> bool:
        return power in self.getPowers()

    def setPower(self, power: str):
        db.exec("update user set power = ? where uid=?", (power, self.uid))

    def getGroups(self) -> set[str]:
        return set(db.exec("select user_group from user where uid=?", (self.uid,)).fetchall()[0][0].split(','))

    def addGroup(self, new_group: str):
        current_group = self.getGroups()
        new_group = current_group | {new_group}  # type: ignore
        self.setGroup(','.join(new_group))

    def removeGroup(self, remove_group: str):
        current_group = self.getGroups()
        new_group = current_group - {remove_group}  # type: ignore
        self.setPower(','.join(new_group))

    def setGroup(self, group: str):
        db.exec("update user set user_group = ? where uid=?", (group, self.uid))

    def isInGroup(self, group: str) -> bool:
        return group in self.getGroups()

    def getLastLoginIP(self) -> str | None:
        return db.exec("select last_login_ip from user where uid=?", (self.uid,)).fetchall()[0][0]

    def setLastLoginIP(self, last_login_ip: str):
        db.exec("update user set last_login_ip = ? where uid=?",
                (last_login_ip, self.uid))

    def getEmail(self) -> str | None:
        email=db.exec("select email from user where uid=?",
                        (self.uid,)).fetchall()[0][0]
        email=None if email == "" else email
        return email

    def setEmail(self, email: str | None):
        email=None if email == "" else email
        db.exec("update user set email = ? where uid=?",
                (email, self.uid))

    def getPreferences(self) -> dict:
        return json.loads(db.exec("select preferences from user where uid=?", (self.uid,)).fetchall()[0][0])

    def getPreference(self, preference_key: str):
        return self.getPreferences()[preference_key]

    def setPreference(self, preference_key: str, value):
        cur=self.getPreferences()
        cur.update({preference_key: value})
        self.setPreferences(json.dumps(cur))

    def setPreferences(self, preferences: str):
        db.exec("update user set preferences = ? where uid=?",
                (preferences, self.uid))

    def updateFlaskId(self):
        fid=sha256(
            f"{self.getUid()}-{self.getUsername()}-{self.getPassword()}")
        assert (self.getUserByFlaskId(fid) is None)
        db.exec("update user set flask_id = ? where uid=?", (fid, self.uid))

    def getFlaskId(self) -> str:
        return db.exec("select flask_id from user where uid=?", (self.uid,)).fetchall()[0][0]
        # 生成的 ID 必须在每次更改密码后改变

    def getResetPasswordToken(self):
        """
        生成重置密码时的 token
        """
        return sha256('p'.join(self.getFlaskId()))

    def UserResetPassword(self):
        MailUtil.sendResetPasswordMail(nickname=self.getNickname(),
                                       url=Config.FRONTEND_PASSWORD_RESET_PATH+"?" +
                                       urllib.parse.urlencode(  # type: ignore
                                           {"token": self.getResetPasswordToken(), "username": self.getUsername()}),
                                       email=self.getEmail())  # type: ignore

    @ property
    def id(self):
        return self.getFlaskId()  # for Flask-Login

    @ classmethod
    def UserLogin(cls, username: str, password: str, ip_address: str):
        user = User.getUserByUsername(username)
        if (user is None) or (not user.isUserExist()) or (not user.verifyPassword(password)):
            result = False
        else:
            result = True
        db.exec(
            "INSERT INTO login_attempt (username, time, result, ip_address) VALUES(?,?,?,?)", (username, int(time.time()), 1 if result else 0, ip_address))
        if Config.FAIL2BAN.ENABLED:
            cls.UserLoginFail2Ban(ip_address)
        if result:
            user.setLastLoginIP(ip_address)  # type: ignore
        return result

    @classmethod
    def UserLoginFail2Ban(cls, ip_address: str):
        fail_counts = len(db.exec("select 1 from login_attempt where ip_address=? and time>=? and result=0",
                                  (ip_address, int(time.time())-Config.FAIL2BAN.TIME_RANGE)).fetchall())
        if fail_counts >= Config.FAIL2BAN.WRONG_COUNT:
            raise PasswordWrongTooMuchError


def power_required(power: str | list | tuple | set):
    def power_required_inner(f):
        @functools.wraps(f)
        def decorated_function(*args, **kws):
            u: User = flask_login.current_user  # type: ignore
            if type(power) is str:
                if not u.hasPower(power):
                    raise PermissionDeniedError
            elif type(power) in (list, tuple, set):  # 以 or 的方式判断是否具有任一权限
                if not any(u.hasPower(p) for p in power):
                    raise PermissionDeniedError
            else:
                raise TypeError
            return f(*args, **kws)
        return decorated_function
    return power_required_inner

