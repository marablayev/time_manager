# Generated by Django 3.1 on 2021-01-25 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_management', '0006_event_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='employees_notified',
        ),
        migrations.RemoveField(
            model_name='event',
            name='force_notify',
        ),
        migrations.AddField(
            model_name='eventconfirmation',
            name='notified',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
