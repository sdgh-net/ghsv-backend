from . import user
from . import default
from . import system
from . import supervision
from . import statistic


def init(fapp):  # fapp: flask app
    user.init_app(fapp)
    default.init_app(fapp)
    system.init_app(fapp)
    supervision.init_app(fapp)
    statistic.init_app(fapp)
