import os
import logging

from django.conf import settings
from django.utils import timezone

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)


from employees.models import Employee, Company
from time_management import ActivityStatus
from time_management.models import EmployeeActivity

from .models import TelegramReplyTemplate
from .handlers import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class BotUpdater(CoreHandler, EventsHandler, ProfileHandler, StatsHandler, TasksHandler,
                 TimeManagementHandler, NewsHandler, Updater):
    def __init__(self, token, *args, **kwargs):
        persistence_file = os.path.join(settings.MEDIA_ROOT, 'bot_persistence_file')
        persistence = PicklePersistence(filename=persistence_file)
        super(BotUpdater, self).__init__(
            token, persistence=persistence, use_context=True, *args, **kwargs)

        self.set_commands()
        self.reply_manager = TelegramReplyTemplate

        dp = self.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.MAIN_MENU: self.get_time_management_handlers(),
                self.AUTH: self.get_auth_handlers(),
                self.STARTING: self.get_starting_shift_handlers(),
                self.ABSENCE: self.get_absence_handlers(),
                self.PROFILE: self.get_profile_handlers(),
                self.STATS_PAGE: self.get_stats_handers(),
                self.EVENTS_PAGE: self.get_event_handlers(),
                self.TASKS_PAGE: self.get_tasks_handlers(),
                self.NEWS_PAGE: self.get_news_handlers(),
            },
            fallbacks=[
                CommandHandler('start', self.start)
            ],
            persistent=True,
            name='main_conversation'
        )

        dp.add_handler(conv_handler)
        dp.add_handler(CallbackQueryHandler(self.event_accepted, pattern='^event_will_come_(-?[0-9]+)$'),)
        dp.add_handler(CallbackQueryHandler(self.event_rejected, pattern='^event_will_not_come_(-?[0-9]+)$'),)
        dp.add_handler(CallbackQueryHandler(self.task_done, pattern='^task_done_(-?[0-9]+)$'),)
        dp.add_handler(MessageHandler(Filters.text, self.undefined_cmd_msg))

    def set_commands(self):
        bot = self.bot
        commands_raw = [
            {'command': 'start', 'description': 'Начать общение с ботом'}
        ]
        bot.set_my_commands([BotCommand(**comm) for comm in commands_raw])


def bot_init(token):
    """
    Method to initialize bot updater
    """
    updater = BotUpdater(token)

    return updater
