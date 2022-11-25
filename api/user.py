from flask import request, redirect, url_for
from User import User, power_required
import flask_login
import Return_Code as RC
from FlaskError import GroupIdNonExistError, InvalidArgumentsError, PasswordMismatchError, PermissionDeniedError, UserExistError, UserIdNonExistError, UserNonExistError
from Functions import ret, verify_comma_values, get_user_ip


def init_app(fapp, *arg):
    global app
    app = fapp
    job()


def job():
    @app.route("/user/new", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def user_new():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        params = {"username", "nickname", "password", "power", "user_group"}
        for i in params:
            if i not in args:
                raise InvalidArgumentsError(f"未提供 {i} 属性")
        if not verify_comma_values(args["power"]):
            raise InvalidArgumentsError("power 属性出现特殊字符")
        if not verify_comma_values(args["user_group"]):
            raise InvalidArgumentsError("user_group 属性出现特殊字符")
        return ret(User.new(username=args.get("username"),  # type: ignore
                            nickname=args.get("nickname"),  # type: ignore
                            password=args.get("password"),  # type: ignore
                            power=args.get("power"),  # type: ignore
                            user_group=args.get("user_group"),  # type: ignore
                            email=args.get("email", None)).toAPI())  # type: ignore

    @app.route("/user/modify", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def user_modify():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if "uid" not in args or not args["uid"].isdigit():
            raise InvalidArgumentsError("属性 uid 应为数字")
        u = User(int(args["uid"]))

        if u is None or not u.isUserExist():
            raise UserIdNonExistError(args["uid"])
        if "power" in args:
            if not verify_comma_values(args["power"]):
                raise InvalidArgumentsError("power 属性出现特殊字符")
        if "user_group" in args:
            if not verify_comma_values(args["user_group"]):
                raise InvalidArgumentsError("user_group 属性出现特殊字符")
        changed_attr = {}
        if "username" in args:
            u.setUsername(args["username"])
            changed_attr.update({"username": args["username"]})
        if "nickname" in args:
            u.setNickname(args["nickname"])
            changed_attr.update({"nickname": args["nickname"]})
        if "password" in args:
            u.setPassword(args["password"])
            changed_attr.update({"password": None})
        if "power" in args:
            u.setPower(args["power"])
            changed_attr.update({"power": args["power"]})
        if "user_group" in args:
            u.setGroup(args["user_group"])
            changed_attr.update({"user_group": args["user_group"]})
        return ret(changed_attr)

    @app.route("/user/delete", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def user_delete():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if not ("username" in args) ^ ("uid" in args):
            raise InvalidArgumentsError("只能提供一个用户查找属性")
        if "username" in args:
            u = User.getUserByUsername(args["username"])
        else:
            if not args["uid"].isdigit():
                raise InvalidArgumentsError("属性 uid 应为数字")
            u = User(int(args["uid"]))
        if u is None or not u.isUserExist():
            raise UserIdNonExistError(args["uid"])
        u.delete()
        return ret()

    @app.route("/user/list", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def user_list():
        result = [i.toAPI() for i in User.listUser()]
        return ret(result)

    @app.route("/user/group/new", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def user_group_new():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        params = {"group_id", "group_name", "power"}
        for i in params:
            if i not in args:
                raise InvalidArgumentsError(f"未提供 {i} 属性")
        if not verify_comma_values(args["power"]):
            raise InvalidArgumentsError("power 属性出现特殊字符")
        if not verify_comma_values(args["group_id"], no_comma=True, no_empty_str=True):
            raise InvalidArgumentsError("group_id 属性出现特殊字符")
        User.newGroup(group_id=args.get("group_id"),  # type: ignore
                      group_name=args.get("group_name"),  # type: ignore
                      power=args.get("power"))  # type: ignore
        return ret()

    @app.route("/user/group/modify", methods=["GET", "POST"])
    @flask_login.login_required
    @power_required("admin")
    def user_group_modify():
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if "group_id" not in args:
            raise InvalidArgumentsError("属性 group_id 未提供")
        if User.getGroupName(args["group_id"]) is None:
            raise GroupIdNonExistError(args["group_id"])
        if "power" in args:
            if not verify_comma_values(args["power"]):
                raise InvalidArgumentsError("power 属性出现特殊字符")
        changed_attr = {}
        if "power" in args:
            User.changeGroupPower(args["group_id"], args["power"])
            changed_attr.update({"power": args["power"]})
        if "group_name" in args:
            User.changeGroupName(args["group_id"], args["group_name"])
            changed_attr.update({"group_name": args["group_name"]})
        return ret(changed_attr)

    @ app.route("/user/info", methods=["GET", "POST"])
    @ flask_login.login_required
    def user_info():
        u: User = flask_login.current_user  # type: ignore
        if request.method == 'GET':
            args = request.args
        else:
            args = request.form
        if "username" in args:
            if not u.hasPower("admin"):
                raise PermissionDeniedError
            u = User.getUserByUsername(args["username"])  # type: ignore
            if u is None:
                raise UserNonExistError(args["username"])
        elif "uid" in args:
            u = User(args["uid"])  # type: ignore
            if u is None or not u.isUserExist():
                raise UserIdNonExistError(args["uid"])
        result = u.toAPI()
        if "uid" in args and not u.hasPower("admin"):  # 对 uid 获取用户特判
            result = {"uid": u.getUid(), "nickname": u.getNickname()}
        return ret(result)

    @ app.route('/user/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return '''
                <form action='login' method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='text' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                </form>
                '''
        try:
            username = request.form['username']
            password = request.form['password']
        except KeyError:
            raise InvalidArgumentsError("未提供用户名或密码")
        if User.UserLogin(username, password, ip_address=get_user_ip(request)):  # type: ignore
            u: User = User.getUserByUsername(username)  # type: ignore
            flask_login.login_user(
                u, remember=True)
            return ret(u.toAPI())
        raise PasswordMismatchError

    @ app.route('/user/send_reset_password_mail', methods=['GET', 'POST'])
    def send_reset_password_mail():
        if request.method == 'GET':
            return '''
                <form action='send_reset_password_mail' method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='text' name='email' id='email' placeholder='email'/>
                    <input type='submit' name='submit'/>
                </form>
                '''
        try:
            username = request.form['username']
            email = request.form['email']
        except KeyError:
            raise InvalidArgumentsError("未提供用户名或邮箱")
        u = User.getUserByUsername(username)
        if u is None or u.isUserExist() is False or u.getEmail() != email:
            return ret()  # 防止猜测邮箱
        u.UserResetPassword()
        return ret()

    @ app.route('/user/user_reset_password', methods=['GET', 'POST'])
    def user_reset_password():
        if request.method == 'GET':
            return '''
                <form action='user_reset_password' method='POST'>
                    <input type='text' name='username' id='username' placeholder='username'/>
                    <input type='text' name='token' id='token' placeholder='token'/>
                    <input type='text' name='password' id='password' placeholder='password'/>
                    <input type='submit' name='submit'/>
                </form>
                <script>
                    function getQueryVariable(variable) {
                        var query = window.location.search.substring(1);
                        var vars = query.split("&");
                        for (var i=0;i<vars.length;i++) {
                            var pair = vars[i].split("=");
                            if(pair[0] == variable){return pair[1];}
                        }
                        return "";
                    }
                    document.getElementById(
                        "token").value = getQueryVariable("token");
                    document.getElementById(
                        "username").value = getQueryVariable("username");
                </script>
                '''
        try:
            username = request.form['username']
            token = request.form['token']
            password = request.form['password']
        except KeyError:
            raise InvalidArgumentsError("未提供 token 或密码")

        ip: str = get_user_ip(request)  # type: ignore
        User.UserLogin(username, token, ip_address=ip)
        # 加个记录
        u = User.getUserByUsername(username)
        error = PasswordMismatchError("token 错误")
        if u is None or not u.isUserExist():
            raise error
        if u.getResetPasswordToken() != token:
            raise error
        u.setPassword(password)
        return ret()

    @ app.route('/user/logout', methods=['GET', 'POST'])  # 登出
    @ flask_login.login_required
    def logout():
        flask_login.logout_user()
        return ret()

#    @app.route('/power_a')
#    @flask_login.login_required
#    @power_required("a")
#    def power_a():
#        u: User = flask_login.current_user  # type: ignore
#        return 'Powered in as: ' + u.__repr__()  # type: ignore
