from django.db import models

from employees.models import Employee


class Task(models.Model):
    employee = models.ForeignKey(
        Employee,
        related_name="created_tasks",
        on_delete=models.CASCADE
    )
    all_employees = models.BooleanField(default=False)
    employees_to_notify = models.ManyToManyField(
        Employee, related_name="tasks_in_notification")
    employees_notified = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    text = models.TextField()
    due_time = models.DateTimeField(null=True, blank=True)


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
    done = models.BooleanField(null=True, blank=True)
