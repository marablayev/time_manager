import calendar
import xlsxwriter
from datetime import datetime, timedelta

from django.utils import timezone
from django.contrib import admin
from django.http import HttpResponse

from .models import Company, Employee, EmployeeActivity



def calculate_hours(start, end):
    if start and end:
        start, end = [datetime.combine(datetime.min, t) for t in [start, end]]
        diff = end - start
        return diff
    return timedelta(0)


def write_to_xlxs(modeladmin, request, queryset):
    current_date = timezone.localdate()
    employees = Employee.objects.all().order_by('company')

    monthrange = calendar.monthrange(current_date.year, current_date.month)
    days = []
    print(monthrange, current_date.year, current_date.month)
    for day in range(1, monthrange[1] + 1):
        date = current_date.replace(day=day)
        days.append(date.strftime('%m/%d/%Y'))
        print(date)


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
            value = calculate_hours(start, end)
            total_hours += timedelta(seconds=value.total_seconds())
            worksheet.write(row, col, str(value))
            col += 1
        worksheet.write(row, col, str(total_hours))
        col = 2
        row += 1

    workbook.close()
    return response

write_to_xlxs.short_description = 'Экспорт данных'


class EmployeeActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee')
    readonly_fields = ('date', )
    actions = (write_to_xlxs, )

    def has_add_permission(self, request, obj=None):
        return False

    # def changelist_view(self, request, extra_context=None):
    #     """Override change_weights_action to accept without selecting instances"""
    #     if 'action' in request.POST and request.POST['action'] == 'write_to_xlxs':
    #         post = request.POST.copy()
    #         for param in EmployeeActivity.objects.all()[:1]:
    #             post.update({admin.ACTION_CHECKBOX_NAME: str(param.id)})
    #         request._set_post(post)
    #     return super(EmployeeActivityAdmin, self).changelist_view(request, extra_context)


admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(EmployeeActivity, EmployeeActivityAdmin)
