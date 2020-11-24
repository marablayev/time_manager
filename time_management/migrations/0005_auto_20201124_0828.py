# Generated by Django 3.1 on 2020-11-24 02:28

import django.contrib.postgres.fields
import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('time_management', '0004_auto_20200825_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employeeactivity',
            options={'ordering': ('-date',)},
        ),
        migrations.AlterField(
            model_name='employeeactivity',
            name='date',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AlterField(
            model_name='employeeactivity',
            name='pauses',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ranges.DateRangeField(blank=True, null=True), blank=True, default=list, size=None),
        ),
    ]
