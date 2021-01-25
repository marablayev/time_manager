from django.db.models.signals import post_save
from django.dispatch import receiver

from employees.models import Employee
from task_management.models import Task, TaskConfirmation


@receiver(post_save, sender=Task)
def task_post_save(sender, instance: Task, created, *args, **kwargs):
    employees = instance.employees_to_notify.all()
    if instance.all_employees:
        employees = Employee.objects.all()

    employees = employees.exclude(task_confirmations__task=instance)

    for employee in employees:
        confirmation = TaskConfirmation.objects.create(task=instance, employee=employee)
        confirmation.notify_employee()
