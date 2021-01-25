from django.db.models import Q
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

    def get_news_handlers(self):
        return self.get_profile_handlers() + [
            CallbackQueryHandler(self.news_get, pattern='^news_item_get_(-?[0-9]+)$'),
        ]

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

    def my_news(self, update, context):
        from news_management.models import News
        if update.callback_query:
            query = update.callback_query
            query.answer()
            chat = query.message.chat
        else:
            chat = update.message.chat

        employee = Employee.objects.filter(chat_id=chat.id).first()
        newss = News.objects.filter(Q(employees_to_notify=employee) | Q(all_employees=True)).distinct()
        if not newss.exists():
            msg = update.message.reply_text(
                self.reply_manager.get_message('no_newss_reply'), parse_mode='HTML',)
            return

        self.render_news(chat.id, context, newss)
        return self.NEWS_PAGE

    def render_news(self, chat_id, context, newss, index=0):
        news = newss[index]
        max_index = newss.count() - 1
        context.user_data['latest_newss_index'] = index
        markup = get_markup('get_news_markup', index, max_index, news.id)

        image = news.image
        message = f"{news.title}\n\n{news.text}"
        if news.employee:
            message += f"\n<b>Владелец: </b>{news.employee.full_name}"

        if image:
            msg = self.bot.send_photo(
                chat_id, photo=image, caption=message,
                reply_markup=markup, parse_mode='HTML')
        else:
            msg = self.bot.send_message(
                chat_id, text=message, reply_markup=markup, parse_mode='HTML')


    def news_get(self, update, context):
        from news_management.models import News
        query = update.callback_query
        query.answer()
        *args, index = query.data.split('_')
        index = int(index)

        employee = Employee.objects.filter(chat_id=query.message.chat.id).first()
        newss = News.objects.filter(Q(employees_to_notify=employee) | Q(all_employees=True)).distinct()
        if newss.count() > 1:
            self.bot.delete_message(query.message.chat.id, query.message.message_id)
            self.render_news(query.message.chat.id, context, newss, index)
