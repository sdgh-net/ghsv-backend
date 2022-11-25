from io import TextIOWrapper
from time import time, localtime, strftime
import os
import sys
from Config import Config
from Functions import ensureDir


class _LogUtil:
    logFileName = ""
    logFile: TextIOWrapper | None = None
    logFileFullPath = ""
    types = ["SILENT", "DEBUG", "VERBOSE", "INFO", "WARNING", "ERROR", "FATAL"]

    def __init__(self):
        ensureDir(Config.PATHS.LOG_DIR)
        self.logFileName = "log-"+self.getFmtTime("%m-%d-%H-%M-%S")+".txt"
        self.logFileFullPath = os.path.join(
            Config.PATHS.LOG_DIR, self.logFileName)
        if Config.STORE_LOG_TO_FILE:
            self.logFile = open(self.logFileFullPath,
                                "w",
                                encoding="utf-8")

    def getFmtTime(self, fmt):
        return strftime(fmt, localtime(time()))

    def log(self, *arg, sep: str = " ", end: str = "\n", _type: str = "INFO"):
        _type = "["+_type.upper()+"]"
        _type = "{:<12}".format(_type)
        finstr = "{} {}    {}{}"\
            .format(_type,
                    self.getFmtTime('%m-%d %H:%M:%S'),
                    sep.join([str(i) for i in arg]),
                    end)
        print(finstr, end="", file=sys.stderr)
        if Config.STORE_LOG_TO_FILE:
            self.logFile.write(finstr)  # type: ignore
            self.logFile.flush()  # type: ignore

    def debug(self, *arg, **kwarg):
        kwarg["_type"] = "DEBUG"
        self.log(*arg, **kwarg)

    def verbose(self, *arg, **kwarg):
        kwarg["_type"] = "VERBOSE"
        self.log(*arg, **kwarg)

    def info(self, *arg, **kwarg):
        kwarg["_type"] = "INFO"
        self.log(*arg, **kwarg)

    def warning(self, *arg, **kwarg):
        kwarg["_type"] = "WARNING"
        self.log(*arg, **kwarg)

    def error(self, *arg, **kwarg):
        kwarg["_type"] = "ERROR"
        self.log(*arg, **kwarg)

    def fatal(self, *arg, **kwarg):
        kwarg["_type"] = "FATAL"
        self.log(*arg, **kwarg)

    def __del__(self):
        if self.logFile is not None and not self.logFile.closed:
            self.logFile.close()

    def delete(self):
        if self.logFile is not None and not self.logFile.closed:
            self.logFile.close()
        try:
            os.remove(self.logFileFullPath)
        except:
            pass


LogUtil = _LogUtil()
