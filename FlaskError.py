
import Return_Code as RC


class CustomFlaskErr(Exception):
    status_code = 400
    msg = None
    return_code = -1
    payload = None
    extra = None

    def __init__(self, return_code, status_code=None, payload=None, extra=None):
        Exception.__init__(self)
        self.return_code = return_code
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.extra = extra

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['result'] = self.return_code
        rv['message'] = RC.MSG.get(self.return_code, "unknown error")
        if self.msg is not None:
            rv['message'] = self.msg
        if self.extra is not None:
            rv['extra'] = self.extra
        return rv


class UserStatusError(CustomFlaskErr):
    def __init__(self):
        raise NotImplementedError


class UserExistError(UserStatusError):
    def __init__(self, username: str):
        self.msg = f"用户 {username} 已存在！"
        self.status_code = 409
        self.return_code = RC.USER_EXIST


class UserNonExistError(UserStatusError):
    def __init__(self, username: str):
        self.msg = f"用户 {username} 不存在！"
        self.status_code = 404
        self.return_code = RC.USER_NON_EXIST


class UserIdNonExistError(UserNonExistError):
    def __init__(self, uid: str | int | None):
        self.msg = f"用户ID {uid} 不存在！"
        self.status_code = 404
        self.return_code = RC.USER_NON_EXIST


class SupervisionStatusError(CustomFlaskErr):
    def __init__(self):
        raise NotImplementedError


class SupervisionExistError(SupervisionStatusError):
    def __init__(self, name: str):
        self.msg = f"监督名 {name} 已存在！"
        self.status_code = 409
        self.return_code = RC.SUPERVISION_EXIST


class SupervisionNonExistError(SupervisionStatusError):
    def __init__(self, name: str):
        self.msg = f"监督名 {name} 不存在！"
        self.status_code = 404
        self.return_code = RC.SUPERVISION_NON_EXIST


class SupervisionIdNonExistError(SupervisionStatusError):
    def __init__(self, sid: str | int | None):
        self.msg = f"监督ID {sid} 不存在！"
        self.status_code = 404
        self.return_code = RC.SUPERVISION_NON_EXIST


class IdeaStatusError(CustomFlaskErr):
    def __init__(self):
        raise NotImplementedError


class IdeaIdNonExistError(IdeaStatusError):
    def __init__(self, sid: str | int | None):
        self.msg = f"意见ID {sid} 不存在！"
        self.status_code = 404
        self.return_code = RC.IDEA_NON_EXIST


class IdeaCompletedError(IdeaStatusError):
    def __init__(self, content: str|None):
        self.msg = f"意见内容“{content}”已处理完成！"
        self.status_code = 403
        self.return_code = RC.IDEA_LOCKED


class PermissionDeniedError(CustomFlaskErr):
    def __init__(self, msg: str | None = None):
        self.status_code = 403
        self.return_code = RC.PREMISSION_DENIED
        if msg is not None:
            self.msg = msg


class InvalidArgumentsError(CustomFlaskErr):
    def __init__(self, msg: str | None = None):
        self.status_code = 400
        self.return_code = RC.INVALID_ARGUMENTS
        if msg is not None:
            self.msg = msg


class PasswordMismatchError(CustomFlaskErr):
    def __init__(self, msg: str | None = None):
        self.status_code = 401
        self.return_code = RC.PASSWORD_MISMATCH
        if msg is not None:
            self.msg = msg


class PasswordWrongTooMuchError(CustomFlaskErr):
    def __init__(self, msg: str | None = None):
        self.status_code = 403
        self.return_code = RC.PASSWORD_WRONG_TOO_MUCH
        if msg is not None:
            self.msg = msg


class APINotImplementedError(CustomFlaskErr):
    def __init__(self, msg: str | None = None):
        self.status_code = 501
        self.return_code = RC.NOT_IMPLEMENTED
        if msg is not None:
            self.msg = msg


class GroupIdNonExistError(CustomFlaskErr):
    def __init__(self, groud_id: str | int | None):
        self.msg = f"用户组ID {groud_id} 不存在！"
        self.status_code = 404
        self.return_code = RC.GROUP_NON_EXIST


class GroupIdExistError(CustomFlaskErr):
    def __init__(self, groud_id: str | int | None):
        self.msg = f"用户组ID {groud_id} 已存在！"
        self.status_code = 409
        self.return_code = RC.GROUP_EXIST
