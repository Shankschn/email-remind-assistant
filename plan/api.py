import re

from shanks import mail
from shanks.format import middle_brackets_chinese_to_english
from shanks.simple_time import *
from .models import *


def get_users_and_emails(notice):
    task = notice.task
    emails = []
    executors = []
    checkers = []
    for executor in task.executor.all():
        emails.append(executor.email)
        executors.append('{}{}<{}>'.format(executor.last_name, executor.first_name, executor.email))
    for checker in task.checker.all():
        emails.append(checker.email)
        checkers.append('{}{}<{}>'.format(checker.last_name, checker.first_name, checker.email))
    return ','.join(executors), ','.join(checkers), list(set(emails))


def update_task_time_nodes(notice):

    temp = get_users_and_emails(notice)[2]
    temp.insert(0, time_to_str(notice.notice_time_actual))

    task = notice.task
    time_nodes = task.time_nodes
    str_time = time_to_str(time_add_day(notice.notice_time_estimated, task.rule.advance_time))
    gs1 = r'(.*?)，'
    fgf = '------'
    gs = str_time + fgf + '已提醒：' + gs1
    search_obj = re.search(gs, time_nodes)
    if search_obj:
        old = search_obj.group()
        new = old + middle_brackets_chinese_to_english(temp) + '，'
        # temp.append(datetime.datetime.today())
    else:
        old = str_time + fgf + '未提醒'

        new = str_time + fgf + '已提醒：' + middle_brackets_chinese_to_english(temp) + '，'
    # print(old, new, time_nodes)
    new_time_nodes = re.sub(old, new, time_nodes)

    task.time_nodes = new_time_nodes
    task.save()


def test_update_task_time_nodes():
    notice = Notice.objects.first()
    update_task_time_nodes(notice)


def send_notice_mail(notice):
    is_success = False
    task = notice.task
    users_and_emails = get_users_and_emails(notice)
    creator = '{}{}<{}>'.format(task.creator.last_name, task.creator.first_name, task.creator.email)
    recipients = users_and_emails[2]
    executors = users_and_emails[0]
    creators = users_and_emails[1]
    recipients.insert(0, 'admin@creditpharma.cn')
    plan_time = time_to_str(time_add_day(date_to_time_max(notice.notice_time_estimated.date()), task.rule.advance_time))
    body = '''
任务名称：{0}——{1}
任务时间：{5}
任务创建人：{2}
任务执行人：{3}
任务确认人：{4}

任务即将进行，请执行人与确认人合理安排时间，并于北京时间 {5} 前执行和确认相关任务。
    '''.format(task.name, task.rule.name, creator, executors, creators, plan_time)

    topic = notice.name + '——即将进行，任务预计提醒时间：' + time_to_str(notice.notice_time_estimated)
    if mail.send_mail_creditpharma_cn(topic, recipients, body):
        notice.notice_time_actual = today()
        notice.is_email = True
        notice.save()
        update_task_time_nodes(notice)
        is_success = False
    return is_success
