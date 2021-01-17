import phonenumbers

from phonenumbers.phonenumberutil import NumberParseException
from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from django.utils import timezone

from employees.models import Employee, Company
from time_management import ActivityStatus
from time_management.models import EmployeeActivity
from ..markups import get_markup


class CoreHandler:
    # Bot main states
    MAIN_MENU, AUTH, STARTING, ABSENCE, PROFILE, STATS_PAGE = range(100, 106)
    # Bot end state
    END = ConversationHandler.END

    def get_auth_handlers(self):
        return [
            CommandHandler('start', self.start),
            MessageHandler(Filters.contact, self.authorize),
            MessageHandler(Filters.text, self.authorize)
        ]

    def start(self, update, context):
        chat = update.message.chat
        if self.check_user(chat):
            self.render_main_menu(update, context)
            return self.MAIN_MENU

        user = update.message.from_user
        text = self.reply_manager.get_message("welcome_message_reply")
        text = text.format(name=user.first_name or user.username)
        update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())

        keyboard = [
            [KeyboardButton(self.reply_manager.get_message('share_phone_button'), request_contact=True)]
        ]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            text=self.reply_manager.get_message("phone_prompt_reply"),
            reply_markup=markup
        )

        return self.AUTH

    def render_main_menu(self, update, context, text=None):
        if update.callback_query:
            query = update.callback_query
            query.answer()
            chat = query.message.chat
        else:
            chat = update.message.chat

        current_date = timezone.localdate()
        employee = Employee.objects.filter(chat_id=chat.id).first()
        activity, _ = EmployeeActivity.objects.get_or_create(
                            employee=employee, date=current_date)
        status = activity.status or ActivityStatus.FINISHED
        shift_change_keys = [
            KeyboardButton(self.reply_manager.get_message('start_shift_button')),
            KeyboardButton(self.reply_manager.get_message('absent_button'))
        ]
        if status == ActivityStatus.WORKING:
            shift_change_keys = [
                KeyboardButton(self.reply_manager.get_message('finish_shift_button'))
            ]

        keyboard = [
            shift_change_keys,
            [
                KeyboardButton(self.reply_manager.get_message('make_action_button')),#'Выбрать действие'), < ==== # Создать задачу
                                                                                                             # Создать событие
                KeyboardButton(self.reply_manager.get_message('profile_button'))#'Профиль(0)') <===# Статистика
                                                                                                # Мои задачи(0)
                                                                                                # Мои События(0)
                                                                                                # Изменить профиль < === Телефон, Имя фамилия, Компания
            ],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if text is None:
            text = "Главное меню"
        if update and update.callback_query:
            bot = query.bot
            # bot.delete_message(chat.id, query.message.message_id)
            bot.send_message(chat.id, text=text, reply_markup=reply_markup)
        elif update:
            update.message.reply_text(text=text, reply_markup=reply_markup)
        else:
            bot = updater.bot
            bot.send_message(chat_id, text=text, reply_markup=reply_markup)

        return self.MAIN_MENU

    def authorize(self, update, context):
        if update.message.contact:
            phone = update.message.contact.phone_number
        else:
            phone = update.message.text

        if phone[0] != '+':
            phone = f"+{phone}"

        try:
            phonenumbers.parse(phone, None)
        except NumberParseException as e:
            msg = update.message.reply_text(
                self.reply_manager.get_message('phone_prompt_reply'), parse_mode='HTML'
            )
            return

        employee = Employee.objects.filter(phone=phone).first()

        if not employee:
            msg = update.message.reply_text(
                self.reply_manager.get_message('user_not_found_reply'), parse_mode='HTML'
            )
            return

        elif employee.chat_id and int(employee.chat_id) != update.message.chat.id:
            msg = update.message.reply_text(
                self.reply_manager.get_message('already_signed_in_reply'), parse_mode='HTML'
            )
            return

        employee.chat_id = update.message.chat.id
        employee.save()
        EmployeeActivity.objects.get_or_create(employee=employee)

        self.render_main_menu(update, context, self.reply_manager.get_message("successful_login"))
        return self.MAIN_MENU

    def check_user(self, chat):
        return Employee.objects.filter(chat_id=chat.id).exists()

    def undefined_cmd_msg(self, update, context):
        msg = update.message.reply_text(
                self.reply_manager.get_message('undefined_cmd_msg'),
                parse_mode='HTML',)

    def notifier(self, chat_id, message="", image=None, markup=None):
        if image:
            self.bot.send_photo(chat_id, photo=image, caption=message,
                                reply_markup=markup, parse_mode="HTML")
        else:
            self.bot.send_message(chat_id, text=message, reply_markup=markup,
                                  parse_mode="HTML")
