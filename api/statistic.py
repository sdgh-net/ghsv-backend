from Config import Const
from Functions import ret


def init_app(fapp, *arg):
    global app
    app = fapp
    job()


def job():
    ...
