from flask import jsonify
import os
from Config import Config
from hashlib import sha256 as hashlib_sha256


def ensureDir(dirname):
    """
    若目录不存在，则尝试新建
    """
    if os.path.isdir(dirname):
        return 0
    return os.mkdir(dirname)


def ensureFile(filename):
    """
    若文件不存在，则尝试新建
    """
#    filename = filename.replace('\\','/')
    if os.path.dirname(filename) != '':
        ensureDir(os.path.dirname(filename))
    if os.path.isfile(filename):
        return 0
    return open(filename, "w").close()


def api_prefix(aroute):
    """
    给 API 加前缀
    """
    return '/{}/{}'.format(Config.API_PREFIX, aroute.lstrip('/'))


def sha256(rtext: str | bytes) -> str:
    sh = hashlib_sha256()
    btext: bytes = rtext.encode() if isinstance(rtext, str) else rtext
    sh.update(btext)
    return sh.hexdigest()


def ret(data=None):
    """
    快速生成 JSON 正常返回数据
    """
    return jsonify({"result": 0, "data": data})


def verify_comma_values(s: str, no_comma: bool = False, no_empty_str: bool = False) -> bool:
    """
    校验逗号分隔值的正确性，防止出现异常值
    """
    if no_comma:
        if ',' in s:
            return False
    if s == "":
        return not no_empty_str
    ALLOW_ALPHABET = "1234567890-_qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM,"
    if (s.strip(ALLOW_ALPHABET) == "") and ('' not in s.split(",")):
        return True
    return False


def verify_integer(s: str) -> bool:
    """
    保证数字字符串 >=1
    """
    if s == "-1":
        return True
    return s.isdigit()


def rm(filename: str) -> None:
    """
    删除文件
    """
    if os.path.isfile(filename):
        os.remove(filename)


def getTempFileName(prefix: str = "") -> str:
    """
    获取临时文件文件名
    """
    s: str = prefix+""
    while s == prefix+"" or os.path.isfile(s):
        s = prefix+os.path.join(Config.PATHS.TEMP_DIR, sha256(os.urandom(32)))
    ensureFile(s)
    return s


def get_user_ip(request) -> str:
    """
    获取用户 IP
    """
    if not Config.USE_NGINX:
        return request.remote_addr
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        raise Exception("X-Real-IP not found")
