from datetime import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from time_management import ActivityStatus
from time_management.models import EmployeeActivity, Employee
from bot.bot import bot_init

class Command(BaseCommand):
    help = 'Runbot'

    def handle(self, *args, **options):
        updater = bot_init(settings.BOT_TOKEN)
        self.updater = updater
        current = timezone.localtime()
        current_date = timezone.localdate()

        employees = Employee.objects.all()
        for employee in employees:
            activity, _ = EmployeeActivity.objects.get_or_create(
                                employee=employee, date=current_date)

            if time(8, 0) <= current.time() < time(19, 0):
                self.start_notify(employee, activity)
            elif time(19,0) <= current.time():
                self.finish_notify(employee, activity)


    def start_notify(self, employee, activity):
        if activity.status != ActivityStatus.NEW:
            return
        try:
            bot = self.updater.bot
            bot.send_message(
                employee.chat_id,
                'Вы не начали рабочий день. Пожалуйста, нажмите на кнопку [Начать рабочий день]')
        except:
            pass #noqa

    def finish_notify(self, employee, activity):
        if activity.status != ActivityStatus.WORKING:
            return

        try:
            bot = self.updater.bot
            bot.send_message(
                employee.chat_id,
                'Вы не завершили рабочий день. Пожалуйста, нажмите на кнопку [Завершить рабочий день]')
        except:
            pass #noqa
