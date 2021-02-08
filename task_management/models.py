from django.conf import settings
from django.db import models

from employees.models import Employee
from bot.bot import bot_init

def tasks_photo_path(instance, filename):
    return f"tasks/{filename}"


class Task(models.Model):
    class Meta:
        ordering = ("-id", )
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    employee = models.ForeignKey(
        Employee,
        related_name="created_tasks",
        on_delete=models.CASCADE
    )
    all_employees = models.BooleanField(default=False)
    employees_to_notify = models.ManyToManyField(
        Employee, related_name="tasks_in_notification", blank=True)
    name = models.CharField(max_length=255)
    text = models.TextField()
    due_time = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=tasks_photo_path)

    def __str__(self):
        return f"{self.name}"


class TaskConfirmation(models.Model):
    task = models.ForeignKey(
        Task,
        related_name="confirmations",
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee,
        related_name="task_confirmations",
        on_delete=models.CASCADE
    )
    notified = models.BooleanField(default=False, null=True, blank=True)
    done = models.BooleanField(null=True, blank=True)

    def notify_employee(self):
        updater = bot_init(settings.BOT_TOKEN)
        updater.task_notify(self.task, [self.employee])
        self.notified = True
        self.save()

    def __str__(self):
        return f"{str(self.task)}. {self.employee.full_name}"
