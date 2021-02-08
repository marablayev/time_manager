from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from django.utils import timezone

from employees.models import Employee, Company
from time_management import ActivityStatus
from time_management.models import EmployeeActivity, AbsenseExcuse

from ..markups import get_markup


class TimeManagementHandler:
    def get_time_management_handlers(self):
        start_text = self.reply_manager.get_message('start_shift_button')
        finish_text = self.reply_manager.get_message('finish_shift_button')
        absent_text = self.reply_manager.get_message('absent_button')
        make_action_text = self.reply_manager.get_message('make_action_button')
        profile_text = self.reply_manager.get_message('profile_button')

        return [
            CommandHandler('start', self.start),
            MessageHandler(Filters.regex(f'^({start_text})|({finish_text})$'), self.start_shift),
            MessageHandler(Filters.regex(f'^({absent_text})$'), self.absent_today),
            MessageHandler(Filters.regex(f'^({make_action_text})$'), self.actions_page),
            MessageHandler(Filters.regex(f'^({profile_text})$'), self.profile_page),
        ]

    def get_starting_shift_handlers(self):
        return [
            CommandHandler('start', self.start),
            CallbackQueryHandler(self.now_selected, pattern='^now_selected$'),
        ]

    def get_absence_handlers(self):
        return [
            CallbackQueryHandler(self.absence_excuse_entered, pattern='^absence_excuse_(-?[0-9]+)$')
        ]

    def start_shift(self, update, context):
        chat = update.message.chat

        current_date = timezone.localdate()
        employee = Employee.objects.filter(chat_id=chat.id).first()

        activity, _ = EmployeeActivity.objects.get_or_create(
                            employee=employee, date=current_date)
        if activity.status == ActivityStatus.FINISHED:
            text = self.reply_manager.get_message('already_finished_reply')
            self.render_main_menu(update, context, text)
            return self.MAIN_MENU

        text = self.reply_manager.get_message('start_shift_confirm_prompt_reply')
        keyboard = [
            [InlineKeyboardButton(self.reply_manager.get_message('start_shift_confirm_button'), callback_data='now_selected')]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text, reply_markup=markup)
        return self.STARTING


    def now_selected(self, update, context):
        query = update.callback_query
        query.answer()
        chat = query.message.chat

        current_date = timezone.localdate()
        current_time = timezone.localtime()
        employee = Employee.objects.filter(chat_id=chat.id).first()
        activity, _ = EmployeeActivity.objects.get_or_create(
                            employee=employee, date=current_date)

        resp_text = self.reply_manager.get_message('successful_started_reply')
        if activity.status != ActivityStatus.WORKING:
            activity.start_time = current_time.time()
            activity.status = ActivityStatus.WORKING
        else:
            activity.finish_time = current_time.time()
            activity.status = ActivityStatus.FINISHED
            resp_text = self.reply_manager.get_message('successful_finished_reply')
        activity.save()

        self.render_main_menu(update, context, resp_text)
        return self.MAIN_MENU


    def absent_today(self, update, context):
        chat = update.message.chat

        current_date = timezone.localdate()
        employee = Employee.objects.filter(chat_id=chat.id).first()
        activity, _ = EmployeeActivity.objects.get_or_create(
                            employee=employee, date=current_date)
        if activity.status == ActivityStatus.FINISHED:
            text = self.reply_manager.get_message('already_finished_reply')
            self.render_main_menu(update, context, text)
            return self.MAIN_MENU

        excuses = AbsenseExcuse.objects.all()
        markup = get_markup('absence_markup', excuses)
        update.message.reply_text(self.reply_manager.get_message('absense_excuse_reply'), reply_markup=markup)
        return self.ABSENCE


    def absence_excuse_entered(self, update, context):
        query = update.callback_query
        query.answer()
        chat = query.message.chat
        *args, excuse_id = query.data.split('_')

        current_date = timezone.localdate()
        employee = Employee.objects.filter(chat_id=chat.id).first()
        activity, _ = EmployeeActivity.objects.get_or_create(
                            employee=employee, date=current_date)

        activity.absent = True
        activity.status = ActivityStatus.FINISHED
        activity.absence_excuse_id = excuse_id
        activity.save()
        text = self.reply_manager.get_message('absense_excuse_entered_reply')
        self.render_main_menu(update, context, text)
        return self.MAIN_MENU
