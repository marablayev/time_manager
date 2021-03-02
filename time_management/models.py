from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField, DateRangeField

from employees.models import Employee
from . import ActivityStatus


class AbsenseExcuse(models.Model):
    class Meta:
        ordering = ('-id', )
        verbose_name = "Причина отсуствия"
        verbose_name_plural = "Причины отсуствия"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Vacation(models.Model):
    class Meta:
        ordering = ('-id', )

    employee = models.ForeignKey(
        Employee, related_name='vacations', on_delete=models.CASCADE)
    start_date = models.DateField()
    finish_date = models.DateField()


class EmployeeActivity(models.Model):
    class Meta:
        verbose_name = "Активность сотрудника"
        verbose_name_plural = "Активность сотрудников"
        unique_together = ("employee", "date")
        ordering = ("-date", )

    employee = models.ForeignKey(
        Employee, related_name='activities', on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    finish_time = models.TimeField(null=True, blank=True)
    date = models.DateField(default=timezone.localdate, editable=False)
    absent = models.BooleanField(default=False)
    absence_excuse = models.ForeignKey(
        AbsenseExcuse, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
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


class Holiday(models.Model):
    """
    Model to store holiday data.
    """
    name = models.CharField("Наименование", max_length=255)
    dates = DateRangeField("Даты С-По")

    class Meta:
        verbose_name = "Праздник"
        verbose_name_plural = "Праздники"

    def __str__(self):
        return self.name


class HolidayMoved(models.Model):
    """
    If saturday or sunday moved to another day, it should be saved in moved_from field
    """
    holiday = models.ForeignKey(
        verbose_name="Праздник", to=Holiday, on_delete=models.CASCADE)
    moved_from = models.DateField("Перенесен с")

    class Meta:
        verbose_name = "Перенесенная дата"
        verbose_name_plural = "Перенесенные даты"

    def __str__(self):
        return f"{self.holiday.name} - {self.moved_from}"
