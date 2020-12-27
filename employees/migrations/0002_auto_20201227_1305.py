# Generated by Django 3.1 on 2020-12-27 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name': 'Компания/Отдел', 'verbose_name_plural': 'Компании/Отделы'},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'verbose_name': 'Сотрудник', 'verbose_name_plural': 'Сотрудники'},
        ),
        migrations.AlterField(
            model_name='employee',
            name='chat_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
