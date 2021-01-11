# Generated by Django 3.1 on 2021-01-11 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0007_remove_company_bot_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('all_employees', models.BooleanField(default=False)),
                ('employees_notified', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('due_time', models.DateTimeField(blank=True, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to='employees.employee')),
                ('employees_to_notify', models.ManyToManyField(related_name='tasks_in_notification', to='employees.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='TaskConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('done', models.BooleanField(blank=True, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_confirmations', to='employees.employee')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmations', to='task_management.task')),
            ],
        ),
    ]
