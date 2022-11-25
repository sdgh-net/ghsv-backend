from flask import request, redirect, send_file, url_for
from ExportUtil import DOCX_PREFIX, exportSupervisionToDocx
from Idea import Idea
from User import User, power_required
import flask_login
from FlaskError import APINotImplementedError, IdeaCompletedError, IdeaIdNonExistError, IdeaStatusError, InvalidArgumentsError, PermissionDeniedError, SupervisionIdNonExistError, SupervisionNonExistError, UserExistError
from Functions import getTempFileName, ret, verify_comma_values, verify_integer
from Supervision import Supervision
import json
import time


def init_app(fapp, *arg):
    global app
    app = fapp
    job()


def job():
    @app.route("/supervision/list", methods=["GET", "POST"])
    @flask_login.login_required
    def supervision_list():
        result = [i.toAPI() for i in Supervision.listSupervision()]
        return ret(result)

    @app.route("/supervision/info", methods=["GET", "POST"])
    @flask_login.login_required
    def supervision_info():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if "name" in args:  # 先使用 name，再使用 id
            u = Supervision.getSupervisionByName(args["name"])
            if u is None or not u.isSupervisionExist():
                raise SupervisionNonExistError(args["name"])
        elif "sid" in args:
            u = Supervision(int(args["sid"]))
            if u is None or not u.isSupervisionExist():
                raise SupervisionIdNonExistError(args["sid"])
        result = u.toAPI()  # type: ignore
        return ret(result)

    @app.route("/supervision/delete", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def supervision_delete():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if not ("name" in args) ^ ("sid" in args):
            raise InvalidArgumentsError("必须只提供一个监督查找属性")
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        u.delete()
        return ret()

    @app.route("/supervision/new", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def supervision_new():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        params = {"name", "until", "target_group"}
        for i in params:
            if i not in args:
                raise InvalidArgumentsError(f"未提供 {i} 属性")
        if not verify_integer(args.get("until")):  # type: ignore
            raise InvalidArgumentsError("until 属性应为数字")
        if not verify_comma_values(args.get("target_group")):  # type: ignore
            raise InvalidArgumentsError("target_group 属性错误")
        return ret(Supervision.new(name=args.get("name"),  # type: ignore
                                   until=args.get("until"),  # type: ignore
                                   target_group=args.get("target_group"),).toAPI())  # type: ignore

    @app.route("/supervision/modify", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def supervision_modify():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if not ("name" in args) ^ ("sid" in args):
            raise InvalidArgumentsError("必须只提供一个监督查找属性")
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        # 检测参数合法性
        if "until" in args:
            if not verify_integer(args.get("until")):  # type: ignore
                raise InvalidArgumentsError("until 应为数字")
        if "target_group" in args:
            if not verify_comma_values(args.get("target_group")):  # type: ignore
                raise InvalidArgumentsError("target_group 属性错误")
        changed_attr = {}
        if "name" in args:
            u.setName(args["name"])
            changed_attr.update({"name": args["name"]})
        if "until" in args:
            if not verify_integer(args.get("until")):  # type: ignore
                raise InvalidArgumentsError("until 应为数字")
            u.setUntil(int(args["until"]))
            changed_attr.update({"until": args["until"]})
        if "target_group" in args:
            if not verify_comma_values(args.get("target_group")):  # type: ignore
                raise InvalidArgumentsError("target_group 属性错误")
            u.setGroup(args.get("target_group"))  # type: ignore
            changed_attr.update({"password": None})
        return ret(changed_attr)

    @app.route("/supervision/statistic", methods=["GET", "POST"])
    @flask_login.login_required
    def supervision_statistic():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if "name" in args and "sid" in args:
            raise InvalidArgumentsError("未提供监督查找属性")
        if "name" not in args and "sid" not in args:  # 返回全局信息
            return ret(Supervision.getOverallStatistic())
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        return ret(u.getStatistic())

    @app.route("/supervision/export", methods=["GET", "POST"])
    @flask_login.login_required
    def supervision_export():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if "format" not in args:
            raise InvalidArgumentsError("未提供 format 属性")
        fmt: str = args["format"]
        if fmt not in ["json", "docx"]:
            raise InvalidArgumentsError("format 属性不正确")
        if "name" in args and "sid" in args:
            raise InvalidArgumentsError("不能同时提供两个监督查找属性")
        if "name" not in args and "sid" not in args:  # 返回全局信息
            if fmt == "json":
                res = []
                for u in Supervision.listSupervision():
                    res.append(u.exportToJson())
                return ret(res)
            elif fmt == "docx":
                raise InvalidArgumentsError("不能导出全局监督信息")
            else:
                raise APINotImplementedError("错误的 format 值未被检测！")
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        if fmt == "json":
            return ret(u.exportToJson())
        elif fmt == "docx":
            filename = getTempFileName(prefix=DOCX_PREFIX)
            exportSupervisionToDocx(filename, u)
            return send_file(filename, as_attachment=True, download_name=f"{u.getName()}反馈.docx")
        else:
            raise APINotImplementedError("错误的 format 值未被检测！")
        return ret()

    @app.route("/supervision/get_ideas", methods=["GET", "POST"])
    @flask_login.login_required
#    @power_required("class")  # 防止部门和管理员进行更新
    def supervision_get_ideas():
        """
        用于班级查看本班/全部的监督
        """
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        show_all = False
        if "show_all" in args:
            show_all = True
        if not ("name" in args) ^ ("sid" in args):
            raise InvalidArgumentsError("必须只提供一个监督查找属性")
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        if show_all:
            kwarg = {}
        else:  # 仅显示本班提交的
            kwarg = {"proponent": flask_login.current_user.getUid()  # type: ignore
                     }
        res = [i.toAPI() for i in Idea.listIdea(**kwarg
                                                ) if i.getStatus() != Idea.Const.IDEA_DELETED]
        return ret(res)

    @app.route("/supervision/list_ideas", methods=["GET", "POST"])
    @flask_login.login_required
#    @power_required("apartment")
    def supervision_list_ideas():
        """
        用于部门对监督进行管理
        """
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if not ("name" in args) ^ ("sid" in args):
            raise InvalidArgumentsError("必须只提供一个监督查找属性")
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        res = [i.toAPI() for i in Idea.listIdea(
            target=flask_login.current_user.getUid()) if i.getStatus() != Idea.Const.IDEA_DELETED]  # type: ignore
        return ret(res)

    @app.route("/supervision/update_ideas", methods=["GET", "POST"])
    @flask_login.login_required
#    @power_required("class")  # 防止部门和管理员进行更新
    def supervision_update_ideas():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if not ("name" in args) ^ ("sid" in args):
            raise InvalidArgumentsError("必须只提供一个监督查找属性")
        if "name" in args:
            u = Supervision.getSupervisionByName(args["name"])
        else:
            if not args["sid"].isdigit():
                raise InvalidArgumentsError("属性 sid 应为数字")
            u = Supervision(int(args["sid"]))
        if u is None or not u.isSupervisionExist():
            raise SupervisionIdNonExistError(args["sid"])
        if "ideas" not in args:
            raise InvalidArgumentsError("未提供 ideas")
        try:
            ideas = json.loads(args["ideas"])
            if type(ideas) is not list:
                raise ValueError
        except ValueError:
            raise InvalidArgumentsError("ideas 属性应为 JSON 数组")
        uid = flask_login.current_user.getUid()  # type: ignore
        sid: int = u.getSid()  # type: ignore
        curtime = int(time.time())
        req_exist_ideas=[]
        for idea in ideas:
            if type(idea) is not dict:
                raise InvalidArgumentsError("每个 idea 属性应为 dict")
            try:
                iid: int = int(idea["iid"])
                content: str = idea["content"]
                if iid != -1 and iid <= 0:
                    raise ValueError
            except KeyError:
                raise InvalidArgumentsError("每个 idea 必须含有 iid 与 content 参数")
            except ValueError:
                raise InvalidArgumentsError("iid 属性非合法 int 值")
            if type(content) is not str:
                raise InvalidArgumentsError("content 属性非合法 str 值")
            try:
                target: int = int(idea["target"])
                if not User(target).isUserExist():
                    raise InvalidArgumentsError("target 用户不存在")
            except KeyError:
                raise InvalidArgumentsError("每个 idea 必须含有 target 参数")
            except ValueError:
                raise InvalidArgumentsError("target 属性非合法 int 值")
            if iid != -1:
                idea = Idea(iid)
                if not idea.isIdeaExist():
                    raise IdeaIdNonExistError(iid)
                if idea.getProponent() != uid:
                    raise PermissionDeniedError(f"意见IID {iid} 所有者非本用户")
                if idea.getStatus() != Idea.Const.IDEA_UNPROCESSED:
                    raise IdeaCompletedError(idea.getContent())
                req_exist_ideas.append(iid)
        # 删除云端没有的意见
        delete_ideas = [Idea(i) for i in Idea.listIdea(proponent=uid,sid=sid) if Idea(i).getStatus() != Idea.Const.IDEA_DELETED and Idea(i).getIid() not in req_exist_ideas]
        for idea in delete_ideas:
            if idea.getStatus() != Idea.Const.IDEA_UNPROCESSED:
                raise IdeaCompletedError(idea.getContent())
        for idea in delete_ideas:
            idea.delete()
        new_ideas = []
        for idea in ideas:
            if type(idea) is not dict:
                raise InvalidArgumentsError("每个 idea 属性应为 dict")
            try:
                iid: int = int(idea["iid"])
                content: str = idea["content"]
                if iid != -1 and iid <= 0:
                    raise ValueError
            except KeyError:
                raise InvalidArgumentsError("每个 idea 必须含有 iid 与 content 参数")
            except ValueError:
                raise InvalidArgumentsError("iid 属性非合法 int 值")
            if type(content) is not str:
                raise InvalidArgumentsError("content 属性非合法 str 值")
            try:
                target: int = int(idea["target"])
                if not User(target).isUserExist():
                    raise InvalidArgumentsError("target 用户不存在")
            except KeyError:
                raise InvalidArgumentsError("每个 idea 必须含有 target 参数")
            except ValueError:
                raise InvalidArgumentsError("target 属性非合法 int 值")
            if iid == -1:
                idea = Idea.new(proponent=uid, target=target,
                                content=content, sid=sid, time=curtime, status=0)
                iid: int = idea.getIid()  # type: ignore
            else:
                idea = Idea(iid)
                if not idea.isIdeaExist():
                    raise IdeaIdNonExistError(iid)
                if idea.getProponent() != sid:
                    raise PermissionDeniedError(f"意见IID {iid} 所有者非本用户")
                if idea.getStatus() != Idea.Const.IDEA_UNPROCESSED:
                    raise IdeaCompletedError(idea.getContent())
                idea.setContent(content)
            new_ideas.append(idea.toAPI())
        return ret(new_ideas)

    @app.route("/supervision/reply_idea", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required(("apartment", "admin"))
    def supervision_reply_idea():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        # 验证 iid
        if "iid" not in args:
            raise InvalidArgumentsError("必须提供 iid 属性")
        if not args["iid"].isdigit():
            raise InvalidArgumentsError("属性 iid 应为数字")
        iid: int = int(args["iid"])
        u = Idea(iid)
        if u is None or not u.isIdeaExist() or u.getStatus() != Idea.Const.IDEA_DELETED:
            raise IdeaIdNonExistError(iid)
        if u.getTarget() != flask_login.current_user.getUid():  # type: ignore
            raise PermissionDeniedError("意见IID {iid} 目标非本用户")
        # 验证 status
        try:
            status: int = int(args["status"])
            if status not in Idea.Const.ALL_IDEA_STATUS:
                raise ValueError
        except KeyError:
            raise InvalidArgumentsError("必须提供 status 属性")
        except ValueError:
            raise InvalidArgumentsError("status 属性非法")
        # 根据 status 处理
        if status == Idea.Const.IDEA_DUPLICATED:
            u.setStatus(status)
        elif status == Idea.Const.IDEA_DELETED:
            u.setStatus(status)
        else:
            if "content" not in args:
                raise InvalidArgumentsError("一般情况必须提供 content 属性")
            content: str = args["content"]
            u.setReply(content)
            u.setStatus(status)
        return ret(u)
