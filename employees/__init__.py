from django.db.models import TextChoices

default_app_config = 'employees.apps.EmployeesConfig'


class EmployeeRoles(TextChoices):
    MANAGER = "manager", "Менеджер"
    EMPLOYEE = "employee", "Сотрудник"
    ADMIN = "admin", "Админ"
