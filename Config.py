# modified for public
import os
import platform


class Config:
    #    BASE_ADDRESS = "http://127.0.0.1:8903"  # 运行的根路径，后面没有"/"
    FRONTEND_PASSWORD_RESET_PATH = "http://127.0.0.1:8901/reset_password"  # 前端密码重置页面的路径
    BIND_ADDRESS = "127.0.0.1"  # 仅允许使用 nginx 访问
    BIND_PORT = 8903
    API_PREFIX = '/api'.strip('/')  # 目前没用
    DEBUG: bool = True
    FLASK_DEBUG = False  # 仅当 DEBUG 为 True 时生效
    STORE_LOG_TO_FILE: bool = False
    """HTTP_CORS_ORIGINS = ["http://localhost:8901", "http://localhost:8903",
                         "http://localhost:3333", "http://127.0.0.1:3333",
                         "http://127.0.0.1:8901", "http://127.0.0.1:8903"]"""
    # 有了 nginx，这里就不需要额外配置
    # SSL_CERT = ("assets/private/cert.pem", "assets/private/key.key")
    # 证书路径与密钥路径的二元**tuple**，设为 None 以禁用 SSL
    # 这边建议用 nginx
    USE_NGINX = True  # 是否在用 nginx，决定 IP 地址获取方式

    class FAIL2BAN:
        ENABLED = True  # 密码多次出错时暂时冻结 IP 地址
        TIME_RANGE = 3*60  # 最近多长时间内，以秒为单位
        WRONG_COUNT = 20  # 单位时间内触发冻结的最小密码错误数
        # （也就是每个 TIME_RANGE 内最多可以尝试失败的次数，最后一次到这个次数时的请求直接拦截）

    class PATHS:
        LOG_DIR = "logs"
        DATA_DIR = "data"
        TEMP_DIR = "temp"
        DB_FILE: str = ""

    class DOCX:  # 设置导出的 docx 文件的字体
        FONT_HEADING = u'黑体'
        FONT_APARTMENT_HEADING = u'黑体'
        FONT_NORMAL = u'宋体'

    class SECURE:
        APP_SECURE_KEY: bytes = b'APP_SECURE_KEY' # 注意！为了安全考虑，此项**必须**修改为一个复杂的不公开的值（如：os.urandom(30)），且生产环境全程不能更换

        class MAIL:
            HOST = '127.0.0.1'
            USERNAME = 'USERNAME'
            PASSWORD = 'PASSWORD'

        class MSSQL:
            HOST = '127.0.0.1'
            USERNAME = 'USERNAME'
            PASSWORD = 'PASSWORD'
            DATABASE = 'DATABASE'
            WHITELIST = []


Config.PATHS.DB_FILE = os.path.join(Config.PATHS.DATA_DIR, "ghsv.db")


class Const:
    PROJECT_NAME = "gh-sv"
    VERSION = "v0.1.0"
    CRIST_NAME = "Cristie"
    CRIST_VERSION = "v0.0.1"
    CRIST_MAIL = "cristie@example.com"


def setProductionEnvironment():
    Config.DEBUG = False
    Config.FLASK_DEBUG = False
    Config.STORE_LOG_TO_FILE = True
    Config.BIND_ADDRESS = "127.0.0.1"
    Config.USE_NGINX = True


def isProductionEnv():
    return platform.system() == "Linux"


if isProductionEnv():
    setProductionEnvironment()

assert(isinstance(Config.SECURE.APP_SECURE_KEY), bytes)