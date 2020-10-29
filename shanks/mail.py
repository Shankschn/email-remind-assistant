from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

import smtplib

from django.utils import timezone


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail(sender, serder_password, sender_identity, smtp_server, topic, recipients, body):
    is_mail_success = False
    name = sender_identity
    account = sender
    password = serder_password
    msg_from = _format_addr('%s <%s>' % (name, account))
    msg_subject = Header(topic, 'utf-8').encode()
    smtp = smtplib.SMTP_SSL(smtp_server, 465)
    smtp.login(account, password)
    # smtp.set_debuglevel(1)
    try:
        msg = MIMEMultipart()
        msg['From'] = msg_from
        msg['Subject'] = msg_subject
        if len(recipients) > 1:
            recipient_list = []
            for recipient in recipients:
                recipient_list.append(_format_addr('<%s>' % recipient))
            msg['To'] = ','.join(recipient_list)
        else:
            msg['To'] = _format_addr('<%s>' % recipients)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        smtp.sendmail(account, recipients, msg.as_string())
    except Exception as e:
        msg = '发送邮件，未发送完成，报错：{}, 错误文件：{}, 错误行：{}'.format(e,
                                                         e.__traceback__.tb_frame.f_globals["__file__"],
                                                         e.__traceback__.tb_lineno)
        print(msg)
    else:
        is_mail_success = True
    finally:
        smtp.quit()
    return is_mail_success,


def send_mail_creditpharma_cn(topic, recipients, body):
    sender = '邮箱帐号'
    serder_password = '游戏密码'
    sender_identity = '发件人身份'
    smtp_server = '服务器地址'
    return send_mail(sender, serder_password, sender_identity, smtp_server, topic, recipients, body)
