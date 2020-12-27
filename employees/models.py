from django.db import models

from phonenumber_field.modelfields import PhoneNumberField


class Company(models.Model):
    class Meta:
        verbose_name = "Компания/Отдел"
        verbose_name_plural = "Компании/Отделы"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    company = models.ForeignKey(
        Company, related_name='employees', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    chat_id = models.BigIntegerField(null=True, blank=True)
    phone = PhoneNumberField(unique=True)

    def __str__(self):
        return f"{self.full_name}"
