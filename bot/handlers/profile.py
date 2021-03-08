import inspect

from django.contrib.staticfiles.finders import find as finder

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from employees.models import Employee, Company
from ..markups import get_markup

class ProfileHandler:
    PROFILE_TEMPLATE = inspect.cleandoc("""
    <b>ФИО: </b>  {full_name}
    <b>Телефон: </b>  {phone}
    <b>Дата рождения: </b>  {birthday}
    <b>Компания: </b>  {company}
    <b>Должность: </b>  {occupation}
    <b>О себе: </b>  {bio}
    """)

    def get_profile_handlers(self):
        return [
            CommandHandler('start', self.start),
            MessageHandler(Filters.regex(f'^Главное меню$'), self.start),
            MessageHandler(Filters.regex(f'^Моя статистика$'), self.stats_page),
            MessageHandler(Filters.regex(f'^События$'), self.events_page),
            MessageHandler(Filters.regex(f'^Задачи$'), self.tasks_page),
            MessageHandler(Filters.regex(f'^Новости$'), self.news_page),
            CallbackQueryHandler(self.render_main_menu, pattern='^profile_back_button$'),
        ]

    def profile_page(self, update, context):
        text = self.reply_manager.get_message('profile_page_reply')
        markup = get_markup('profile_page')
        update.message.reply_text(text, reply_markup=markup)

        employee = Employee.objects.get(chat_id=update.message.chat.id)

        photo = employee.photo or open(finder('bot/no_photo.jpg'), 'rb')

        text = self.PROFILE_TEMPLATE.format(**{
            "full_name": employee.full_name,
            "phone": employee.phone.as_e164,
            "birthday": str(employee.birthday) if employee.birthday else "",
            "company": employee.company.name if employee.company else "",
            "occupation": employee.occupation or "",
            "bio": employee.bio or "",
        })

        update.message.reply_photo(
            photo, caption=text, parse_mode="HTML", reply_markup=get_markup("profile_back"))
        return self.PROFILE
