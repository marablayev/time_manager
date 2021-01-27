# Generated by Django 3.1 on 2021-01-27 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_management', '0002_auto_20210126_0057'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ('-id',), 'verbose_name': 'Новость', 'verbose_name_plural': 'Новости'},
        ),
        migrations.AddField(
            model_name='news',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]