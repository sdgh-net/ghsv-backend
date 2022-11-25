import sqlite3
from Config import Config
import threading
from Functions import ensureFile
from LogUtil import LogUtil
import os

TABLE_INITS = {
    "idea": """CREATE TABLE "idea" (
  "iid" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "sid" INTEGER NOT NULL,
  "proponent" integer NOT NULL,
  "target" integer NOT NULL,
  "content" TEXT NOT NULL,
  "reply" TEXT,
  "duplicate_iid" integer,
  "status" integer NOT NULL,
  "time" integer NOT NULL,
  "extra" TEXT NOT NULL DEFAULT '{}'
);""",

    "login_attempt": """CREATE TABLE "login_attempt" (
  "username" TEXT NOT NULL,
  "time" integer NOT NULL,
  "result" integer NOT NULL,
  "ip_address" TEXT NOT NULL
);""",

    "supervision": """CREATE TABLE "supervision" (
  "sid" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "name" text NOT NULL,
  "until" integer NOT NULL,
  "target_group" integer NOT NULL
);""",

    "user": """CREATE TABLE "user" (
  "uid" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
  "username" text NOT NULL,
  "nickname" text NOT NULL,
  "password" text NOT NULL,
  "power" text NOT NULL,
  "user_group" text NOT NULL,
  "last_login_ip" text,
  "email" text,
  "flask_id" text NOT NULL,
  "preferences" text NOT NULL DEFAULT '{}'
);""",
    "user_group": """CREATE TABLE "user_group" (
  "group_id" text NOT NULL PRIMARY KEY,
  "group_name" text NOT NULL,
  "power" text NOT NULL DEFAULT ''
);""", }


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class _DBUtil:
    lock = threading.Lock()
    init_dict = []

    def verify_db(self):
        had_tables = self.get_all_tables()
        for table in self.init_dict:
            if table not in had_tables:
                self.exec(self.init_dict[table])
                LogUtil.error(f"数据库表 {table} 错误，正在重建")

    def __init__(self, db_file: str, dict_data: bool = False, init_dict: dict = {}):
        self.db_file = db_file
        ensureFile(self.db_file)
        self.init_dict = init_dict
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        if dict_data:
            self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()
        self.verify_db()

    def exec(self, *args, **kwargs):
        with self.lock:
            # print(args)
            a = self.c.execute(*args, **kwargs)
            self.conn.commit()
        return a

    def init_with_dict(self, init_dict: dict):
        for v in init_dict.values():
            self.exec(v)

    def get_all_tables(self) -> set:
        return set([i[0] for i in self.exec("select name from sqlite_master where type='table'")])

    def __del__(self):
        self.conn.commit()
        self.conn.close()


db = _DBUtil(Config.PATHS.DB_FILE, init_dict=TABLE_INITS)