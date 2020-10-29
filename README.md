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
修改 shanks\mail.py 文件
~~~
def send_mail_creditpharma_cn(topic, recipients, body):
    sender = '邮箱帐号'
    serder_password = '游戏密码'
    sender_identity = '发件人身份'
    smtp_server = '服务器地址'
    return send_mail(sender, serder_password, sender_identity, smtp_server, topic, recipients, body)
~~~
## 运行服务
~~~
python manage.py runserver
~~~
# 使用说明
先配置规则，再创建任务。
