from django.db import models

from employees.models import Employee
from bot.bot import bot_init


class Event(models.Model):
    class Meta:
        ordering = ("-id", )
        verbose_name = "Событие/Встреча"
        verbose_name_plural = "События/Встречи"

    employee = models.ForeignKey(
        Employee,
        related_name="created_events",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, default='')
    all_employees = models.BooleanField(default=False)
    employees_to_notify = models.ManyToManyField(
        Employee, related_name="events_in_notification")
    employees_notified = models.BooleanField(default=False)
    date_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    place = models.CharField(max_length=255)
    force_notify = models.BooleanField(default=False)

    def notify_employees(self):
        queryset = Employee.objects.all()
        if not self.all_employees:
            queryset = self.employees_to_notify.all()

        updater = bot_init(token)
        updater.event_notify(self, queryset)
        self.employees_notified = True
        self.save()
        EventConfirmation.objects.bulk_create(
            [EventConfirmation(event=self, employee=employee) for employee in queryset],
            batch_size=500
        )


class EventConfirmation(models.Model):
    event = models.ForeignKey(
        Event,
        related_name="confirmations",
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee,
        related_name="event_confirmations",
        on_delete=models.CASCADE
    )
    accepted = models.BooleanField(null=True, blank=True)
