from threading import Thread

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from employees.models import Employee

from ..markups import get_markup


class NewsHandler:

    def news_notify(self, news, employees):
        bot = self.bot
        image = news.image
        message = f"{news.title}\n\n{news.text}"
        if news.employee:
            message += f"\n<b>Владелец: </b>{news.employee.full_name}"

        for employee in employees:
            args = tuple()
            kwargs = {'parse_mode': 'HTML'}
            if image:
                method = bot.send_photo
                args = (employee.chat_id, image)
                kwargs['caption'] = message
            else:
                method = bot.send_message
                args = (employee.chat_id, message)
            f_msg = self.reply_manager.get_message('news_received_reply')
            thread = Thread(target=bot.send_message, args=(employee.chat_id, f_msg))
            thread.start()
            thread = Thread(target=method, args=args, kwargs=kwargs)
            thread.start()
