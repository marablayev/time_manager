# Generated by Django 3.1 on 2021-01-11 06:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0007_remove_company_bot_token'),
        ('event_management', '0002_auto_20210111_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='EventConfirmation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(blank=True, null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_confirmations', to='employees.employee')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmations', to='event_management.event')),
            ],
        ),
    ]
