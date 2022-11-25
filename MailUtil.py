# modified for public
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from Config import Config,Const
from LogUtil import LogUtil


class MAILS:
    gyclass = [f"gy{i}@example.com" for i in range(1, 10+1)]
    geclass = [f"gy{i}@example.com" for i in range(1, 10+1)]
    cc = ["cc@example.com"]
    gyge = []


MAILS.gyge = MAILS.gyclass+MAILS.geclass


def sendEmail(title:str, content:str, sender_mail:str, receivers: list[str], nickname: str, attachments: list[str] = [], Cc: list[str] = [], use_html: bool = False):
    if use_html:
        msg_type = 'html'
    else:
        msg_type = 'plain'
    message = MIMEText(content, msg_type, 'utf-8')
    message['Subject'] = title
    message['From'] = Header(
        nickname, 'utf-8').encode('utf-8') + " " + f"<{sender_mail}>"
    message['To'] = ','.join(set(receivers))
    if len(Cc) != 0:
        message['Cc'] = ','.join(Cc)
    smtpObj = smtplib.SMTP()
    smtpObj.connect(Config.SECURE.MAIL.HOST, 25)
    smtpObj.login(Config.SECURE.MAIL.USERNAME, Config.SECURE.MAIL.PASSWORD)
    send_to = set(receivers+Cc)
    smtpObj.sendmail(
        sender_mail, send_to, message.as_string())  # type: ignore
    smtpObj.quit()
    LogUtil.verbose(f"[发送邮件] “{title}” 至 {send_to}")


def sendResetPasswordMail(nickname: str, url: str, email: str, title: str = "【ghsv】重置密码"):
    content = open("Templates/Mail/reset_password.html",
                   "r", encoding="utf-8").read().format(nickname, url)
    sendEmail(title, content, Const.CRIST_MAIL, [email,], Const.CRIST_NAME, use_html=True)


# sendEmail("title", open(r"D:\a.html", encoding="utf8").read(), "sender@example.com",
#          MAILS.gyclass+MAILS.geclass, "nickname", Cc=MAILS.cc, use_html=True)
