import datetime

from django.utils import timezone
from dateutil.relativedelta import relativedelta


def today():
    return datetime.datetime.today()


def date_to_time_min(date):
    return datetime.datetime.combine(date, datetime.datetime.min.time())


def date_to_time_max(date):
    return datetime.datetime.combine(date, datetime.datetime.max.time())


def date_add_hour(date, hour):
    time = date_to_time_min(date)
    return time + datetime.timedelta(hours=int(hour))


def date_add_day(date, day):
    return date + datetime.timedelta(days=int(day))


def time_add_hour(time, hour):
    return time + datetime.timedelta(hours=int(hour))


def time_add_day(time, day):
    return time + datetime.timedelta(days=int(day))


def time_add_month(time, month):
    return time + relativedelta(months=int(month))


def str_to_time(str_time):
    return datetime.datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")


def time_to_str(time):
    return time.strftime("%Y-%m-%d %H:%M:%S")


def str_add_hour(str_time, hour):
    time_add_hour(str_to_time(str_time), int(hour))


def utc_to_cst_time(time):
    return timezone.localtime(time).strftime("%Y-%m-%d %H:%M:%S")


def time_is_today(time):

    pass


def is_in_range(time, start_time, end_time):
    pass

