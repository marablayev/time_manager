import os
import logging

from django.conf import settings
from django.utils import timezone

from employees.models import Employee, Company
from time_management import ActivityStatus
from time_management.models import EmployeeActivity
from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Bot main states
MAIN_MENU, AUTH, STARTING, ABSENCE = range(100, 104)
# Bot end state
END = ConversationHandler.END


# core methods
def start(update, context):
    chat = update.message.chat
    if check_user(chat):
        render_main_menu(update, context)
        return MAIN_MENU

    user = update.message.from_user
    text = 'Добро пожаловать, {}'.format(user.first_name or user.username)
    update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())

    update.message.reply_text(text='Пожалуйста, введите ваши ФИО: ', reply_markup=ReplyKeyboardRemove())

    return AUTH


def render_main_menu(update, context, text=None):
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
    shift_change_keys = [KeyboardButton('Начать рабочий день'), KeyboardButton('Отсуствую')]
    if status == ActivityStatus.WORKING:
        shift_change_keys = [KeyboardButton('Закончить рабочий день')]

    keyboard = [
        shift_change_keys,
        [KeyboardButton('Моя статистика'), KeyboardButton('Профиль')],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if text is None:
        text = "Главное меню."
    if update and update.callback_query:
        bot = query.bot
        bot.delete_message(chat.id, query.message.message_id)
        bot.send_message(chat.id, text=text, reply_markup=reply_markup)
    elif update:
        update.message.reply_text(text=text, reply_markup=reply_markup)
    else:
        bot = updater.bot
        bot.send_message(chat_id, text=text, reply_markup=reply_markup)

    return MAIN_MENU



def full_name_entered(update, context):
    full_name = update.message.text
    context.user_data['full_name'] = full_name
    companies = Company.objects.all()
    inline_keyboard = []
    for company in companies:
        callback = f'company_{company.id}'
        inline_keyboard.append(
            [InlineKeyboardButton(company.name, callback_data=callback)]
        )
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    update.message.reply_text(text='Выберите организацию: ', reply_markup=inline_markup)


def company_selected(update, context):
    query = update.callback_query
    query.answer()
    chat = query.message.chat
    full_name = context.user_data['full_name']
    *args, company_id = query.data.split("_")

    employee = Employee.objects.create(
        chat_id=chat.id,
        full_name=full_name,
        company_id=company_id)
    EmployeeActivity.objects.create(employee=employee)

    render_main_menu(update, context, "Регистрация прошла успешно.")
    return MAIN_MENU


def check_user(chat):
    return Employee.objects.filter(chat_id=chat.id).exists()



# Main app methods
def start_shift(update, context):
    chat = update.message.chat
    print(update.message)

    current_date = timezone.localdate()
    employee = Employee.objects.filter(chat_id=chat.id).first()
    if update.message.text == '/edit':
        EmployeeActivity.objects.filter(employee=employee, date=current_date).delete()

    activity, _ = EmployeeActivity.objects.get_or_create(
                        employee=employee, date=current_date)
    if activity.status == ActivityStatus.FINISHED:
        text = "Вы уже завершили сегодняшний день. Если есть вопросы, обратитесь к @marablayev.\n\n"\
               "Если хотите перезаписать, введите команду /edit"
        render_main_menu(update, context, text)
        return MAIN_MENU

    text = "Введите время в формате HH:MM(09:55), либо Нажмите на кнопку 'Сейчас'"
    keyboard = [
        [InlineKeyboardButton("Сейчас", callback_data='now_selected')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=markup)
    return STARTING


def time_entered(update, context):
    chat = update.message.chat
    time_str = update.message.text

    current_date = timezone.localdate()
    employee = Employee.objects.filter(chat_id=chat.id).first()
    activity, _ = EmployeeActivity.objects.get_or_create(
                        employee=employee, date=current_date)

    resp_text = 'Вы начали рабочий день. Удачи!:)'

    if activity.status != ActivityStatus.WORKING:
        activity.start_time = time_str
        activity.status = ActivityStatus.WORKING
    else:
        activity.finish_time = time_str
        activity.status = ActivityStatus.FINISHED
        resp_text = 'Спасибо за службу. Иди домой и отдохни!'
    activity.save()

    render_main_menu(update, context, resp_text)
    return MAIN_MENU


def now_selected(update, context):
    query = update.callback_query
    query.answer()
    chat = query.message.chat

    current_date = timezone.localdate()
    current_time = timezone.localtime()
    employee = Employee.objects.filter(chat_id=chat.id).first()
    activity, _ = EmployeeActivity.objects.get_or_create(
                        employee=employee, date=current_date)

    resp_text = 'Вы начали рабочий день. Удачи!:)'
    if activity.status != ActivityStatus.WORKING:
        activity.start_time = current_time.time()
        activity.status = ActivityStatus.WORKING
    else:
        activity.finish_time = current_time.time()
        activity.status = ActivityStatus.FINISHED
        resp_text = 'Спасибо за службу. Иди домой и отдохни!'
    activity.save()

    render_main_menu(update, context, resp_text)
    return MAIN_MENU


def absent_today(update, context):
    chat = update.message.chat

    current_date = timezone.localdate()
    employee = Employee.objects.filter(chat_id=chat.id).first()
    activity, _ = EmployeeActivity.objects.get_or_create(
                        employee=employee, date=current_date)
    if activity.status == ActivityStatus.FINISHED:
        text = "Вы уже завершили сегодняшний день. Если есть вопросы, обратитесь к @marablayev.\n\n"\
               "Если хотите перезаписать, введите команду /edit"
        render_main_menu(update, context, text)
        return MAIN_MENU

    update.message.reply_text('Пожалуйста, опишите причину вашего отсуствия:')
    return ABSENCE


def absence_excuse_entered(update, context):
    chat = update.message.chat
    excuse = update.message.text

    current_date = timezone.localdate()
    employee = Employee.objects.filter(chat_id=chat.id).first()
    activity, _ = EmployeeActivity.objects.get_or_create(
                        employee=employee, date=current_date)

    activity.absent = True
    activity.status = ActivityStatus.FINISHED
    activity.absence_excuse = excuse
    activity.save()
    text = 'Понятно... Возвращайся скорее! Без тебя на работе томно:)'
    render_main_menu(update, context, text)
    return MAIN_MENU


def stats_page(update, context):
    chat = update.message.chat
    text = "Ваша активность за текущий месяц:"

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
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=markup)


# -------------------------
# Utils methods
# -------------------------
def text_entered(update, context):
    text = "Я не понял вас. Пожалуйста, введите то что я понимаю, либо обратитесь к @marablayev"
    render_main_menu(update, context, text)
    return MAIN_MENU


def error_handler(*args, **kwargs):
    print(args, kwargs)


def bot_init(token):
    """
    Method to initialize bot updater
    """
    persistence_file = os.path.join(settings.MEDIA_ROOT, 'bot_persistence_file')
    persistence = PicklePersistence(filename=persistence_file)
    updater = Updater(token, persistence=persistence, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CommandHandler('start', start),
                CommandHandler('edit', start_shift),
                MessageHandler(Filters.regex('^(Начать рабочий день)|(Закончить рабочий день)$'), start_shift),
                MessageHandler(Filters.regex('^(Отсуствую)$'), absent_today),
                MessageHandler(Filters.regex('^(Моя статистика)$'), stats_page),
            ],
            AUTH: [
                CommandHandler('start', start),
                CallbackQueryHandler(company_selected, pattern='^company_(-?[0-9]+)$'),
                MessageHandler(Filters.text, full_name_entered)
            ],
            STARTING: [
                CommandHandler('start', start),
                MessageHandler(Filters.regex('^([0-1][0-9]|2[0-3]):[0-5][0-9]$'), time_entered),
                CallbackQueryHandler(now_selected, pattern='^now_selected$'),
            ],
            ABSENCE: [
                MessageHandler(Filters.text, absence_excuse_entered)
            ]
        },
        fallbacks=[
            CommandHandler('start', start)
        ],
        persistent=True,
        name='main_conversation'
    )

    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, text_entered))
    # dp.add_error_handler(error_handler)
    return updater
    # updater.start_polling()
