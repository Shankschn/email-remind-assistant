from django.contrib import admin, messages

# Register your models here.
from django.db.models.signals import post_save
from django.db.models import Q
from django.dispatch import receiver

from shanks.django_admin_user import import_users
from .api import send_notice_mail
from .models import *
from shanks.simple_time import *


admin.site.site_title = '任务提醒助手'
admin.site.site_header = '任务提醒助手'
admin.site.index_title = '任务烯烃助手'


public_read_only = ['operator', 'operate_time', 'creator', 'create_time']


def operating_log(obj, request):
    if not obj.creator:
        obj.creator = request.user
    obj.operator = request.user
    return obj


# # 一对多关联表编辑,让父表管理配置页面能同时编辑子表,以下的Score为子表(有外键所在的表)
# class Inline(admin.TabularInline):
#     # Score 必须是models.py中的模型名称,大小写必须要匹配.这个模型为子表,以便可以被父表编辑
#     model = Score
#     # 默认显示条目的数量
#     # extra = 5
#
#
# class StudentsAdmin(admin.ModelAdmin):
#     # Inline把ScoreInline关联进来,让父表管理配置页面能同时编辑子表.
#     inlines = [ScoreInline, ]


# @admin.register(People)
# class PeopleAdmin(admin.ModelAdmin):
#     search_fields = ['peopleid', 'name', 'email']
#     readonly_fields = public_read_only
#     pass
#
#     def save_model(self, request, obj, form, change):
#         obj = operating_log(obj, request)
#         obj.save()


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['ruleid', 'name', 'time_nodes', 'time_nodes_type']
    list_filter = ['creator']
    search_fields = ['ruleid', 'name']
    readonly_fields = public_read_only
    save_as = True
    pass

    def save_model(self, request, obj, form, change):
        obj = operating_log(obj, request)
        obj.save()


class TaskFileInline(admin.StackedInline):
    extra = 0
    model = TaskFile
    # exclude = exclude_must
    readonly_fields = public_read_only
    ordering = ['-id']


@admin.register(TaskFile)
class TaskFileAdmin(admin.ModelAdmin):
    list_filter = ['creator']
    search_fields = ['name']
    readonly_fields = public_read_only
    autocomplete_fields = ['task']
    pass

    def save_model(self, request, obj, form, change):
        obj = operating_log(obj, request)
        obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(creator=request.user).distinct()


def time_add_node(def_time, start_time, nodes):
    time_nodes_list = []
    for node in nodes:
        time_nodes_list.append(def_time(start_time, node))
    return time_nodes_list


def get_time_nodes_list(obj):
    nodes = obj.rule.time_nodes.split(',')
    time_nodes_type = obj.rule.time_nodes_type
    start_time = date_add_hour(obj.start_date, obj.hour)
    if time_nodes_type == 0:
        time_nodes_list = time_add_node(time_add_day, start_time, nodes)
    else:
        time_nodes_list = time_add_node(time_add_month, start_time, nodes)
    return time_nodes_list


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['taskid', 'name']
    list_filter = ['creator', 'executor', 'checker', 'start_date', 'end_date']
    autocomplete_fields = ['executor', 'checker', 'rule']
    # list_display = ['format_time_nodes']
    readonly_fields = public_read_only + ['time_nodes', 'end_date']
    inlines = [TaskFileInline]
    save_as = True
    pass

    def save_model(self, request, obj, form, change):
        obj = operating_log(obj, request)

        if change:
            old = Task.objects.get(pk=obj.pk)
            if obj.start_date != old.start_date:
                obj.start_date = old.start_date
                messages.error(request, '已经存在的项目，不能修改开始日期！')
            if obj.rule != old.rule:
                obj.rule = old.rule
                messages.error(request, '已经存在的项目，不能修改提醒规则！')
            if obj.name != old.name:
                obj.name = old.name
                messages.error(request, '已经存在的项目，不能修改任务名称！')
            if obj.hour != old.hour:
                obj.hour = old.hour
                messages.error(request, '已经存在的项目，不能修改提醒时间点！')
            if obj.end_date != old.end_date:
                obj.end_date = old.end_date
                messages.error(request, '已经存在的项目，不能修改结束日期！')
        else:
            time_nodes_list = get_time_nodes_list(obj)
            temp_time_nodes = ''
            fgf = '------'
            hhf = '\n'
            zt = '未提醒'
            for time_node in time_nodes_list:
                temp_time_nodes = temp_time_nodes + time_to_str(time_node) + fgf + zt + hhf
            # obj.time_nodes = mark_safe(temp_time_nodes)
            obj.time_nodes = temp_time_nodes
            obj.end_date = time_nodes_list[-1].date()
        obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(Q(executor=request.user) | Q(checker=request.user) | Q(creator=request.user)).distinct()


@receiver(post_save, sender=Task)
def create_notices(sender, instance, created, raw, using, update_fields, **kwargs):
    print('in create_notices ...')
    print('in create_notices show somethings', sender, instance, created, raw, using, update_fields)
    if created:
        time_nodes_list = get_time_nodes_list(instance)
        for time_node in time_nodes_list:
            print(time_node, type(time_node))
            Notice.objects.create(
                task=instance,
                name='提醒消息——' + instance.name + '：' + instance.rule.name,
                notice_time_estimated=time_add_day(time_node, -instance.rule.advance_time)
            )
    else:
        print('in create_notices nothings to do')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    autocomplete_fields = ['task']
    readonly_fields = ['notice_time_actual', 'is_email']
    actions = ['action_send_notice_email']
    list_display = ['name', 'notice_time_estimated', 'is_email', 'notice_time_actual']
    list_filter = ['task']
    
    def save_model(self, request, obj, form, change):
        obj = operating_log(obj, request)
        obj.save()

    def action_send_notice_email(self, request, queryset):
        for obj in queryset:
            send_notice_mail(obj)
        messages.info(request, '执行完毕。')
    action_send_notice_email.short_description = '发送提醒邮件'


@admin.register(Mgmt)
class MgmtAdmin(admin.ModelAdmin):
    list_display = ['remark', 'is_success', 'operator', 'operate_time']
    list_filter = ['operator']
    actions = ['create_users']
    readonly_fields = public_read_only + ['is_success']
    search_fields = ['remark']

    def save_model(self, request, obj, form, change):
        obj = operating_log(obj, request)
        obj.save()

    def create_users(self, request, queryset):
        for obj in queryset:
            if not obj.is_success:
                is_success = import_users(obj.text)
                if is_success:
                    messages.success(request, '{}——执行完毕。'.format(obj))
                    obj.is_success = True
                    obj.save()
                else:
                    messages.error(request, '{}——执行过程中错误，请排查。'.format(obj))
            else:
                messages.error(request, '{}——已经被成功执行，请勿重复执行。'.format(obj))
    create_users.short_description = '批量添加用户'
