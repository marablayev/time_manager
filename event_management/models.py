from django.db import models

from employees.models import Employee


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
    all_employees = models.BooleanField(default=False)
    employees_to_notify = models.ManyToManyField(
        Employee, related_name="events_in_notification")
    employees_notified = models.BooleanField(default=False)
    date_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    place = models.CharField(max_length=255)
    force_notify = models.BooleanField(default=False)


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
