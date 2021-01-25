import inspect, sys

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)

from bot.models import TelegramReplyTemplate

reply_manager = TelegramReplyTemplate


def get_markup(markup_name, *args, **kwargs):
    method = next((obj for name, obj in inspect.getmembers(sys.modules[__name__])
                        if (inspect.isfunction(obj) and name==markup_name)
                        ), None)
    return method(*args, **kwargs) if method else None


def test_method(test_arg=0):
    return 1 + test_arg


def profile_page():
    keyboard = [
        [
            KeyboardButton('Главное меню'), KeyboardButton('Моя статистика')],
        [
            KeyboardButton('Мои события'), KeyboardButton('Мои задачи')]
    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    return markup


def profile_back():
    keyboard = [
        [InlineKeyboardButton(reply_manager.get_message("back_button"), callback_data="profile_back_button")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    return markup


def stats_page():
    keyboard = [
        [InlineKeyboardButton(reply_manager.get_message("detailed_stats_button"), callback_data="detailed_stats")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    return markup


def get_iterator_keyboard(current, maximum, model):
    prev = current - 1 if current > 0 else maximum
    next = current + 1 if current < maximum else 0
    return [
        [
            InlineKeyboardButton('<', callback_data=f'{model}_item_get_{prev}'),
            InlineKeyboardButton(f'{current + 1}/{maximum + 1}', callback_data=f'empty'),
            InlineKeyboardButton('>', callback_data=f'{model}_item_get_{next}'),
        ]
    ]


def get_event_markup(current, maximum, offer_id) -> InlineKeyboardMarkup:
    keyboard = get_iterator_keyboard(current, maximum, 'events')

    markup = InlineKeyboardMarkup(keyboard)
    return markup


def event_notify_markup(event_id) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(reply_manager.get_message('will_come_button'), callback_data=f'event_will_come_{event_id}'),
            InlineKeyboardButton(reply_manager.get_message('will_not_come_button'), callback_data=f'event_will_not_come_{event_id}'),
        ]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup


def task_notify_markup(task_id) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(reply_manager.get_message('task_done_button'), callback_data=f'task_done_{task_id}'),
        ]
    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup
