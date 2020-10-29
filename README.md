# email-remind-assistant
邮件提醒助手。
# Blog
https://yudelei.com/169.html
# 运行说明
## 描述
email-remind-assistant 是一个电子邮件提醒助手。可以在规定时间通过发送电子邮件来提醒用户。
## 环境
Python 3.7
## 安装 pip 包
~~~
pip install django=2.2.*
pip install mysqlclient
pip install django-simpleui
pip install python-dateutil
~~~
## 配置邮件服务器
修改 shanks\mail.py 文件。
### 注意
邮件 SMTP 服务器需使用 SSL 且端口为标准 465 端口。
~~~
def send_mail_creditpharma_cn(topic, recipients, body):
    sender = '邮箱帐号'
    serder_password = '游戏密码'
    sender_identity = '发件人身份'
    smtp_server = '服务器地址'
    return send_mail(sender, serder_password, sender_identity, smtp_server, topic, recipients, body)
~~~
在 plan/api 中配置并启用 send_notice_mail 的扫送邮箱，所有邮件都将会抄送一份至此邮箱。
~~~
...
def send_notice_mail(notice):
    is_success = False
    task = notice.task
    users_and_emails = get_users_and_emails(notice)
    creator = '{}{}<{}>'.format(task.creator.last_name, task.creator.first_name, task.creator.email)
    recipients = users_and_emails[2]
    executors = users_and_emails[0]
    creators = users_and_emails[1]
    # recipients.insert(0, '抄送邮箱')
...
~~~
## 配置 Django-crontab 定时服务
默认：早 8 点 10 分 至晚 6 点 10 分，每小时检查一次是否有需要通知的邮件。若需修改，在 settings.py 中修改。
~~~
CRONJOBS = [
    ('10 8-18/1 * * *', 'shanks.crontab.my_crontab', '>>/www/txgj/shanks/crontab.log')
]
~~~
修改完成后，添加到到定时任务 crontab 中。
~~~
# 添加定时任务
python manage.py crontab add

# 查看定时任务
python manage.py crontab show

# 查看定时任务
python manage.py crontab remove
~~~
## 运行服务
~~~
python manage.py runserver
~~~
# 使用说明
先配置规则，再创建任务。
