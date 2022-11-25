from FlaskError import CustomFlaskErr, PermissionDeniedError
import flask_login
import api
import os
import sys
from flask import Flask, request, jsonify
from gevent import pywsgi
from Config import Config, Const
from LogUtil import LogUtil
import User
from datetime import timedelta
# from flask_cors import CORS

# chdir to current file's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__)
app.secret_key = Config.SECURE.APP_SECURE_KEY
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
flask_login.config.COOKIE_DURATION = timedelta(days=365*10)  # 记住我有效期 10 年
flask_login.config.COOKIE_SAMESITE = "Strict"
flask_login.config.COOKIE_HTTPONLY = True
User.init_login_manager(login_manager)
login_manager.login_view = 'login'  # type: ignore
# CORS(app, origins=Config.HTTP_CORS_ORIGINS,
#     supports_credentials=True)  # 在 OPTIONS 时设置 CORS


@app.errorhandler(CustomFlaskErr)
def handle_flask_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@login_manager.unauthorized_handler
def unauthorized():
    raise PermissionDeniedError


api.init(app)


if __name__ == "__main__":
    LogUtil.info(f"===== {Const.PROJECT_NAME} {Const.VERSION} =====")
    LogUtil.verbose(f"正在启动服务：http://{Config.BIND_ADDRESS}:{Config.BIND_PORT}")
    if Config.DEBUG:
        argv = {"host": Config.BIND_ADDRESS,
                "port": Config.BIND_PORT, "debug": Config.FLASK_DEBUG}
        # if Config.SSL_CERT is not None:
        #    argv["ssl_context"] = Config.SSL_CERT
        app.run(**argv)
    else:
        argv = {}
        # if Config.SSL_CERT is not None:
        #    argv["certfile"], argv["keyfile"] = Config.SSL_CERT
        server = pywsgi.WSGIServer(
            (Config.BIND_ADDRESS, Config.BIND_PORT), app)  # 无输出
        server.serve_forever()
        app.run()
    # 以上这部分是阻塞的
