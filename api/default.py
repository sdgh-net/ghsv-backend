from flask import request, send_file
from Config import Const


def init_app(fapp, *arg):
    global app
    app = fapp
    job()


def job():
    @app.route("/", methods=["GET", "POST"])
    def test_main_page():
        return f"HELLO from {Const.PROJECT_NAME} {Const.VERSION}!"

    @app.route("/favicon.ico", methods=["GET"])
    def favicon():
        return send_file("assets/favicon.ico")
