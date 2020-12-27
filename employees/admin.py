from django.contrib import admin

from employees.models import Company, Employee


admin.site.register(Company)
admin.site.register(Employee)
