from django.db.models.signals import post_save
from django.dispatch import receiver

from employees.models import Employee
from event_management.models import Event, EventConfirmation


@receiver(post_save, sender=Event)
def event_post_save(sender, instance: Event, created, *args, **kwargs):
    employees = instance.employees_to_notify.all()
    if instance.all_employees:
        employees = Employee.objects.all()

    employees = employees.exclude(event_confirmations__event=instance)

    new_confirmations = [
        EventConfirmation(event=instance, employee=employee) for employee in employees]

    print(employees)
    for employee in employees:
        confirmation = EventConfirmation.objects.create(event=instance, employee=employee)
        confirmation.notify_employee()
