# Generated by Django 3.1 on 2021-01-25 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0009_employee_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ('id',), 'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
    ]