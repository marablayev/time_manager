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
                 TimeManagementHandler, Updater):
    def __init__(self, token, *args, **kwargs):
        persistence_file = os.path.join(settings.MEDIA_ROOT, 'bot_persistence_file')
        persistence = PicklePersistence(filename=persistence_file)
        super(BotUpdater, self).__init__(
            token, persistence=persistence, use_context=True, *args, **kwargs)

        self.set_commands()
        self.reply_manager = TelegramReplyTemplate

        dp = self.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                self.MAIN_MENU: [
                    CommandHandler('start', self.start),
                    MessageHandler(Filters.regex('^(Начать рабочий день)|(Закончить рабочий день)$'), self.start_shift),
                    MessageHandler(Filters.regex('^(Отсуствую)$'), self.absent_today),
                    MessageHandler(Filters.regex('^(Моя статистика)$'), self.stats_page),
                ],
                self.AUTH: [
                    CommandHandler('start', self.start),
                    CallbackQueryHandler(self.company_selected, pattern='^company_(-?[0-9]+)$'),
                    MessageHandler(Filters.text, self.full_name_entered)
                ],
                self.STARTING: [
                    CommandHandler('start', self.start),
                    MessageHandler(Filters.regex('^([0-1][0-9]|2[0-3]):[0-5][0-9]$'), self.time_entered),
                    CallbackQueryHandler(self.now_selected, pattern='^now_selected$'),
                ],
                self.ABSENCE: [
                    MessageHandler(Filters.text, self.absence_excuse_entered)
                ]
            },
            fallbacks=[
                CommandHandler('start', self.start)
            ],
            persistent=True,
            name='main_conversation'
        )

        dp.add_handler(conv_handler)
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
    