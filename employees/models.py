from django.db import models
from django.contrib.auth.models import User

from phonenumber_field.modelfields import PhoneNumberField
from . import EmployeeRoles


def employee_photo_path(instance, filename):
    return f"employees/{filename}"


class Company(models.Model):
    class Meta:
        verbose_name = "Компания/Отдел"
        verbose_name_plural = "Компании/Отделы"

    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        related_name="child_companies",
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    manager = models.ForeignKey(
        "Employee",
        related_name="managing_companies",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ("id", )

    company = models.ForeignKey(
        Company, related_name='employees', on_delete=models.PROTECT)
    role = models.CharField(
        max_length=255, default=EmployeeRoles.EMPLOYEE, choices=EmployeeRoles.choices)
    full_name = models.CharField(max_length=255)
    chat_id = models.BigIntegerField(null=True, blank=True)
    phone = PhoneNumberField(unique=True)
    photo = models.ImageField(null=True, blank=True, upload_to=employee_photo_path)
    photo_card = models.ImageField(null=True, blank=True, upload_to=employee_photo_path)
    birthday = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    user = models.OneToOneField(
        User,
        related_name='employee_profile',
        on_delete=models.SET_NULL,
        null=True, blank=True)

    def __str__(self):
        return f"{self.full_name}"
