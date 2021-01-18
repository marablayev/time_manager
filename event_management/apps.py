from django.apps import AppConfig


class EventManagementConfig(AppConfig):
    name = 'event_management'
    verbose_name = 'Панель Событий'

    def ready(self):
        import event_management.signals
