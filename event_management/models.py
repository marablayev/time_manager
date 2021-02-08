from django.conf import settings
from django.db import models

from employees.models import Employee
from bot.bot import bot_init

def events_photo_path(instance, filename):
    return f"events/{filename}"


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
        Employee, related_name="events_in_notification", blank=True)
    date_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    place = models.CharField(max_length=255)
    image = models.ImageField(null=True, blank=True, upload_to=events_photo_path)
    telegram_group_link = models.URLField(null=True, blank=True)


class EventDocs(models.Model):
    class Meta:
        ordering = ("-id", )
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    event = models.ForeignKey(Event, related_name='docs', on_delete=models.CASCADE)
    file = models.FileField(upload_to=events_photo_path)


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
    notified = models.BooleanField(default=False, null=True, blank=True)
    accepted = models.BooleanField(null=True, blank=True)

    def notify_employee(self):
        updater = bot_init(settings.BOT_TOKEN)
        updater.event_notify(self.event, [self.employee])
        self.notified = True
        self.save()
