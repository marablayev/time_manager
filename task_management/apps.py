from django.apps import AppConfig


class TaskManagementConfig(AppConfig):
    name = 'task_management'
    verbose_name = 'Панель Задач'

    def ready(self):
        import task_management.signals
