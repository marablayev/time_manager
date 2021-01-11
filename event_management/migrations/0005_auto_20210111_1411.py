# Generated by Django 3.1 on 2021-01-11 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0007_remove_company_bot_token'),
        ('event_management', '0004_auto_20210111_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='employees_to_notify',
            field=models.ManyToManyField(related_name='events_in_notification', to='employees.Employee'),
        ),
    ]
