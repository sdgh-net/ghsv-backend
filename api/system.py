from Config import Const
from Functions import ret


def init_app(fapp, *arg):
    global app
    app = fapp
    job()


def job():
    @app.route("/system/version", methods=["GET", "POST"])
    def system_version():
        return ret({Const.PROJECT_NAME: Const.VERSION,
                    Const.CRIST_NAME: Const.CRIST_VERSION})
