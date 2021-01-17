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
