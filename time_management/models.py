from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField, DateRangeField

from . import ActivityStatus
# from .managers import EmployeeManager

class Company(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employee(models.Model):
    company = models.ForeignKey(
        Company, related_name='employees', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    chat_id = models.BigIntegerField(unique=True)

    # objects = EmployeeManager()

    def __str__(self):
        return f"{self.full_name}"


class EmployeeActivity(models.Model):
    class Meta:
        ordering = ("-date", )
    employee = models.ForeignKey(
        Employee, related_name='activity', on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    finish_time = models.TimeField(null=True, blank=True)
    date = models.DateField(default=timezone.localdate, editable=False)
    absent = models.BooleanField(default=False)
    absence_excuse = models.TextField(null=True, blank=True)
    pauses = ArrayField(DateRangeField(null=True, blank=True), default=list, blank=True)
    status = models.CharField(
        max_length=20, default=ActivityStatus.NEW, choices=ActivityStatus.choices)

    def start(self, time=None):
        if not time:
            time = timezone.localtime()
        if not self.start_time:
            self.start_time = time
            self.save()

    def finish(self, time=None):
        if not time:
            time = timezone.localtime()
        if not self.finish_time:
            self.finish_time = time
            self.save()

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"
