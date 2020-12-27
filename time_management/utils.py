import calendar
from datetime import datetime, timedelta

from django.utils import timezone

from time_management.models import HolidayMoved, Holiday


def is_holiday(date=timezone.localdate()):

    is_holiday = Holiday.objects.filter(dates__contains=date).exists()
    is_moved = HolidayMoved.objects.filter(moved_from=date).exists()

    is_holiday = is_holiday or not 0 <= date.weekday() < 5

    return is_holiday and not is_moved


def calculate_total_hours(date=None, day_till=None, day_from=None):
    date = timezone.localdate() if date is None else date
    monthrange = calendar.monthrange(date.year, date.month)
    day_till = monthrange[1] if day_till is None else day_till
    day_from = 1 if day_from is None else day_from

    return sum(8 for d in range(day_from, day_till + 1) if not is_holiday(date.replace(day=d)))


def calculate_work_hours(start, end):
    if start and end:
        start, end = [datetime.combine(datetime.min, t) for t in [start, end]]
        diff = end - start
        return diff
    return timedelta(0)


def get_worked_hours(employee, date=None, day_till=None, day_from=None):
    date = timezone.localdate() if date is None else date
    monthrange = calendar.monthrange(date.year, date.month)
    day_till = monthrange[1] if day_till is None else day_till
    day_from = 1 if day_from is None else day_from
    activities = employee.activities.filter(date__month=date.month)
    return [calculate_work_hours(act.start_time, act.finish_time) for act in activities]


def get_stats(employees=[], date=None):
    date = timezone.localdate() if date is None else date
    total_hours_till_today = calculate_total_hours(date, day_till=date.day)
    total_hours_for_month = calculate_total_hours(date)
    resp = []

    for employee in employees:

        resp_data = {
            "employee_id": employee.id
            "total_hours_till_today": total_hours_till_today,
            "total_hours_for_month": total_hours_for_month,
            "extra_hours": 0,
            "missing_hours": 0,
            "total_worked_hours": get_worked_hours(employee, date=date, day_till=date.day),
            "absent": 0
        }
