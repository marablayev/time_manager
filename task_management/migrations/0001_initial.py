# Generated by Django 3.1 on 2021-03-02 10:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import task_management.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('all_employees', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('due_time', models.DateTimeField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=task_management.models.tasks_photo_path)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
                ('employees_to_notify', models.ManyToManyField(blank=True, related_name='tasks_in_notification', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='TaskConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notified', models.BooleanField(blank=True, default=False, null=True)),
                ('done', models.BooleanField(blank=True, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_confirmations', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmations', to='task_management.task')),
            ],
        ),
        migrations.CreateModel(
            name='AutoTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=task_management.models.tasks_photo_path)),
                ('deletable', models.BooleanField(blank=True, default=True)),
                ('is_active', models.BooleanField(blank=True, default=True)),
                ('all_employees', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_auto_tasks', to=settings.AUTH_USER_MODEL)),
                ('employees_to_notify', models.ManyToManyField(blank=True, related_name='auto_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]
