from django.db import models


class ActivityStatus(models.TextChoices):
    NEW = 'new', 'Новый'
    ABSENT = 'absent', 'Отсуствует'
    WORKING = 'working', 'В работе'
    FINISHED = 'finished', 'Завершен'
