# Generated by Django 3.1 on 2021-01-11 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0005_auto_20210111_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='role',
            field=models.CharField(choices=[('manager', 'Менеджер'), ('employee', 'Сотрудник'), ('admin', 'Админ')], default='employee', max_length=255),
        ),
    ]