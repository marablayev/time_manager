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
