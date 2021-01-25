import inspect

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from django.utils import timezone

from employees.models import Employee
from time_management.models import EmployeeActivity
from time_management.utils import get_stats

from ..markups import get_markup


class StatsHandler:
    STATS_INFO = inspect.cleandoc("""
    <b>Общее за месяц: </b>  {total_hours_for_month}
    <b>До сегодняшнего дня: </b>  {total_hours_till_today}
    <b>Отработанных: </b>  {total_worked_hours}
    <b>Недоработки: </b>  {missing_hours} {missing_hours_emoji}
    <b>Переработки: </b>  {extra_hours}

    * кол-во часов
    """)

    def get_stats_handers(self):
        return self.get_profile_handlers() + [
            CallbackQueryHandler(self.detailed_stats, pattern='^detailed_stats$'),
            CallbackQueryHandler(self.stats_page, pattern='^detailed_stats_back_button$'),
        ]

    def detailed_stats(self, update, context):
        query = update.callback_query
        query.answer()
        chat = query.message.chat
        text = self.reply_manager.get_message('stats_page_reply')

        current_date = timezone.localdate()
        employee = Employee.objects.filter(chat_id=chat.id).first()
        activity, _ = EmployeeActivity.objects.get_or_create(
                            employee=employee, date=current_date)

        activities = EmployeeActivity.objects.filter(
                        employee=employee, date__month=current_date.month
                        ).order_by("date")
        keyboard = []
        for activity in activities:
            act_date = activity.date.strftime('%Y-%m-%d')
            start_time = activity.start_time.strftime('%H:%M') if activity.start_time else 'N/a'
            finish_time = activity.finish_time.strftime('%H:%M') if activity.finish_time else 'N/a'
            keyboard.append(
                [
                    InlineKeyboardButton(act_date, callback_data='empty'),
                    InlineKeyboardButton(f"{start_time} - {finish_time}", callback_data='empty')
                ]
            )
        keyboard.append([InlineKeyboardButton(self.reply_manager.get_message("back_button"), callback_data="detailed_stats_back_button")])
        markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text, reply_markup=markup)

    def stats_page(self, update, context):
        if update.callback_query:
            query = update.callback_query
            query.answer()
            chat = query.message.chat
        else:
            chat = update.message.chat

        current_date = timezone.localdate()
        employee = Employee.objects.filter(chat_id=chat.id).first()
        stats = get_stats([employee])[0]
        stats['missing_hours_emoji'] = ''
        if stats['missing_hours']:
            stats['missing_hours_emoji'] = u'\U00002757'

        text = self.STATS_INFO.format(**stats)
        markup = get_markup('stats_page')

        if update and update.callback_query:
            query.edit_message_text(text, reply_markup=markup, parse_mode='HTML')
        elif update:
            update.message.reply_text(text=text, reply_markup=markup, parse_mode='HTML')

        return self.STATS_PAGE
