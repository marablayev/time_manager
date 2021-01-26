# Generated by Django 3.1 on 2021-01-25 21:11

from django.db import migrations, models
import django.db.models.deletion
import event_management.models


class Migration(migrations.Migration):

    dependencies = [
        ('event_management', '0008_event_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDocs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=event_management.models.events_photo_path)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docs', to='event_management.event')),
            ],
            options={
                'verbose_name': 'Документ',
                'verbose_name_plural': 'Документы',
                'ordering': ('-id',),
            },
        ),
    ]