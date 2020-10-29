import datetime

from plan.api import send_notice_mail
from plan.models import Notice


def my_crontab():
    now = datetime.datetime.now()
    notices = Notice.objects.filter(is_email=False)

    if notices:
        for notice in notices:
            if now > notice.notice_time_estimated:
                if send_notice_mail(notice):
                    # 发送成功日志
                    msg = '{}——{}'.format(notice.name, '邮件提醒，发送成功。')
                else:
                    # 发送失败日志
                    msg = '{}——{}'.format(notice.name, '邮件提醒，发送失败。')
            else:
                # 时间未到，未发送日志
                msg = '{}——{}'.format(notice.name, '邮件提醒，时间未到，无需发送。')
            msg = str(datetime.datetime.now()) + msg
            print(msg)
    else:
        msg = '无 需要发送邮件提醒的通知。'
        msg = str(datetime.datetime.now()) + msg
        print(msg)

