from django.db import models


default_app_config = 'time_management.apps.TimeManagementConfig'

class ActivityStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    ABSENT = 'absent', 'Отсуствует'
    WORKING = 'working', 'В работе'
    FINISHED = 'finished', 'Завершен'
