import calendar
import xlsxwriter
from datetime import datetime, timedelta

from django.utils import timezone
from django.http import HttpResponse

from time_management.models import HolidayMoved, Holiday, EmployeeActivity
from employees.models import Employee


def is_holiday(date=timezone.localdate(), employee=None):

    is_holiday = Holiday.objects.filter(dates__contains=date).exists()
    is_moved = HolidayMoved.objects.filter(moved_from=date).exists()

    is_holiday = is_holiday or not 0 <= date.weekday() < 5
    if employee:
        is_holiday = employee.vacations.filter(
            start_date__gte=date, finish_date__lte=date)

    return is_holiday and not is_moved


def calculate_total_hours(date=None, day_till=None, day_from=None, employee=None):
    date = timezone.localdate() if date is None else date
    monthrange = calendar.monthrange(date.year, date.month)
    day_till = monthrange[1] if day_till is None else day_till
    day_from = 1 if day_from is None else day_from

    return sum(8 for d in range(day_from, day_till + 1) if not is_holiday(date.replace(day=d), employee=employee))


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
    activities = employee.activities.filter(
        date__month=date.month,
        date__day__gte=day_from,
        date__day__lte=day_till
    )

    worked_hours = []
    for day in range(day_from, day_till + 1):
        act = activities.filter(date__day=day).first()
        start, finish = None, None
        if act:
            start, finish = act.start_time, act.finish_time
        worked_hours.append(calculate_work_hours(start, finish))
    return sum(round(h.seconds / 3600, 2) for h in worked_hours)


def get_stats(employees=[], date=None):
    date = timezone.localdate() if date is None else date
    resp = []

    for employee in employees:
        if not employee: continue
        total_hours_till_today = calculate_total_hours(date, day_till=date.day, employee=employee)
        total_hours_for_month = calculate_total_hours(date, employee=employee)
        worked_hours = get_worked_hours(employee, date=date, day_till=date.day)
        diff_hours = round(total_hours_till_today - worked_hours, 2)

        resp_data = {
            "employee_id": employee.id,
            "total_hours_till_today": total_hours_till_today,
            "total_hours_for_month": total_hours_for_month,
            "extra_hours": abs(diff_hours) if diff_hours < 0 else 0,
            "missing_hours": abs(diff_hours) if diff_hours > 0 else 0,
            "total_worked_hours": worked_hours,
            "diff_hours": diff_hours * -1,
            "absent": 0
        }
        resp.append(resp_data)

    return resp


def write_to_xlxs():
    current_date = timezone.localdate()
    employees = Employee.objects.all().order_by('company')

    monthrange = calendar.monthrange(current_date.year, current_date.month)
    days = []
    for day in range(1, monthrange[1] + 1):
        date = current_date.replace(day=day)
        days.append(date.strftime('%m/%d/%Y'))


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="time_manager.xlsx"'
    # Start writing to file
    workbook = xlsxwriter.Workbook(response)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    header_date_format = workbook.add_format()
    merge_format = workbook.add_format()
    merge_format.set_align('center')
    user_format = workbook.add_format()
    row = 0
    col = 2
    for day in days:
        worksheet.write(row, col, day, header_date_format)
        col += 1

    worksheet.write(row, col, 'Итого', header_date_format)

    companies = []
    row = 1
    col = 2
    for employee in employees:
        activities = EmployeeActivity.objects.filter(
                        employee=employee, date__month=current_date.month)
        activities_dict = {
            a.date.strftime('%m/%d/%Y'): a for a in activities
        }
        total_hours = timedelta(0)
        if employee.company.id not in companies:
            worksheet.merge_range(row, 0, row, 1, employee.company.name, merge_format)
            companies.append(employee.company.id)
            row += 1
        worksheet.write(row, 0, employee.full_name, user_format)
        for day in days:
            activity = activities_dict.get(day)
            if activity:
                start, end = activity.start_time, activity.finish_time
            else:
                start, end = None, None
            value = calculate_work_hours(start, end)
            total_hours += timedelta(seconds=value.total_seconds())
            worksheet.write(row, col, str(value))
            col += 1
        worksheet.write(row, col, str(total_hours))
        col = 2
        row += 1

    workbook.close()
    return response
