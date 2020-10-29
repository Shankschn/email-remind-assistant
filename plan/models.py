from django.db import models

import datetime
# Create your models here.
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User


def get_user_full_name(self):
    return '{}{}'.format(self.last_name, self.first_name)


User.add_to_class("__str__", get_user_full_name)


class OperatingAbstract(models.Model):
    """
    类说明：操作抽象类
    如果字段中出现 db_column 表示自定义 数据库字段显示名称
    """
    creator = models.ForeignKey('auth.User', on_delete=models.PROTECT,
                                related_name='%(app_label)s_%(class)s_creator',
                                null=True, blank=True,
                                verbose_name='创建人')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='北京时间。')
    operator = models.ForeignKey('auth.User', on_delete=models.PROTECT,
                                 related_name='%(app_label)s_%(class)s_operator',
                                 null=True, blank=True,
                                 verbose_name='操作人')
    operate_time = models.DateTimeField(auto_now=True, verbose_name='操作时间', help_text='北京时间。')

    class Meta:
        abstract = True
        # 数据库中表名称 默认app_表名
        # db_table = 'History'
        # Django Admin 中显示名名称
        # verbose_name = 'History' # 单数
        # verbose_name_plural = verbose_name # 复数


class Rule(OperatingAbstract):
    ruleid = models.CharField('规则编码', max_length=20, unique=True, null=True)
    name = models.CharField('规则名称', max_length=255, null=True)
    advance_time = models.IntegerField('提醒提前天数', null=True, default=3)
    time_nodes = models.CharField('时间节点', max_length=255, null=True,
                                  help_text='数字。以英文逗号分隔。')
    time_nodes_types = (
        (0, '自然日'),
        (1, '自然月'),
    )
    time_nodes_type = models.IntegerField('时间节点单位', choices=time_nodes_types, default=0, null=True,
                                          help_text='自然日或自然月。默认：自然日。')

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '规则'  # 单数
        verbose_name_plural = '规则列表'  # 复数

    def __str__(self):
        return self.name

#
# class MarkSafeTextField(models.TextField):
#     def formfield(self, **kwargs):
#         kwargs[''] = mark_safe(self.description )


class Task(OperatingAbstract):
    taskid = models.CharField(verbose_name='任务编码', unique=True, max_length=20, null=True)
    name = models.CharField(verbose_name='任务名称', max_length=255, null=True, help_text='创建后，不允许修改。')
    start_date = models.DateField(verbose_name='开始日期', null=True, help_text='创建后，不允许修改。')
    end_date = models.DateField(verbose_name='结束日期', null=True, help_text='创建后，不允许修改。')
    executor = models.ManyToManyField('auth.User', related_name='executor', verbose_name='执行人')
    checker = models.ManyToManyField('auth.User', related_name='checker', verbose_name='确认人')
    rule = models.ForeignKey(Rule, on_delete=models.PROTECT, null=True, verbose_name='提醒规则',
                             help_text='创建后，不允许修改。')
    time_nodes = models.TextField(max_length=1000, null=True, verbose_name='时间节点')
    hour = models.IntegerField(null=True, blank=True, default=9, verbose_name='提醒时间点',
                               help_text='制式：24 小时。发送提醒邮件的时间点。默认为：北京时间 9 点。<br>创建后，不允许修改。')

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '任务'  # 单数
        verbose_name_plural = '任务列表'  # 复数

    def __str__(self):
        return self.name


def task_file_upload_to(instance, filename):
    return '/'.join([instance.task.taskid, filename])


class TaskFile(OperatingAbstract):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, verbose_name='任务名称')
    name = models.CharField(max_length=255, null=True, verbose_name='文件名',
                            help_text='必须填写文件/附件名。')
    file = models.FileField(upload_to=task_file_upload_to, null=True, verbose_name='文件')

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '附件'  # 单数
        verbose_name_plural = '附件中心'  # 复数

    def __str__(self):
        return self.name


class Notice(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, verbose_name='任务')
    name = models.CharField('通知名称', max_length=255, null=True)
    notice_time_estimated = models.DateTimeField(verbose_name='预计通知时间', null=True, help_text='北京时间。')
    notice_time_actual = models.DateTimeField(verbose_name='实际通知时间', null=True, help_text='北京时间。')
    # notice_time_estimated = models.CharField('预计通知时间', max_length=50, null=True)
    # notice_time_actual = models.CharField('实际通知时间', max_length=50, null=True)
    is_email = models.BooleanField('已发送通知邮件', default=False, null=True)

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '通知'  # 单数
        verbose_name_plural = '通知列表'  # 复数

    def __str__(self):
        return self.name


class Mgmt(OperatingAbstract):
    text = models.TextField('内容', null=True,
                            help_text='字段分隔符：——。用户分隔符：##。<br>'
                                      '格式：账号【英文/数字】——邮件地址——密码【字母/数字/标点符号】——名——姓——登陆【0：禁止；1：允许】##<br>'
                                      '例如：zhangsan——zhangsan@domain.com——zhangsan.110——三——张——1##')
    remark = models.CharField('批量添加用户说明', max_length=255, null=True, blank=True)
    is_success = models.BooleanField('已成功执行"批量添加用户"？', default=False, null=True)

    class Meta:
        # 数据库中表名称 默认app_表名
        # db_table = ''
        # Django Admin 中显示名名称
        verbose_name = '管理工具'  # 单数
        verbose_name_plural = '管理工具'  # 复数

    def __str__(self):
        return self.remark

