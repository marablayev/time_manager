import inspect, sys

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, LoginUrl)

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
            KeyboardButton('Главное меню')],
        [
            KeyboardButton('Моя статистика'), KeyboardButton('Мои события')
        ],
        [
            KeyboardButton('Новости'), KeyboardButton('Мои задачи')]
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


def get_task_markup(current, maximum, offer_id) -> InlineKeyboardMarkup:
    keyboard = get_iterator_keyboard(current, maximum, 'tasks')

    markup = InlineKeyboardMarkup(keyboard)
    return markup


def get_news_markup(current, maximum, offer_id) -> InlineKeyboardMarkup:
    keyboard = get_iterator_keyboard(current, maximum, 'news')

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


def actions_page_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Событие/Встреча", login_url=LoginUrl(url='https://172.105.80.130/events-telegram/'))],#callback_data=f'event_create_selected')],
        # [InlineKeyboardButton("Задача", login_url=LoginUrl(url='https://172.105.80.130/tasks-telegram/'))],#callback_data=f'task_create_selected')],
        # [InlineKeyboardButton("Новость", login_url=LoginUrl(url='https://172.105.80.130/news-telegram/'))]#callback_data=f'news_create_selected')],

    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup

def pass_by_image() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Пропустить этот шаг", callback_data=f'pass_by_image')],

    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup

def all_employees_markup(type="all") -> InlineKeyboardMarkup:
    text = "Все пользователи" if type == "all" else "Закончить"
    keyboard = [
        [InlineKeyboardButton(text, callback_data=f'{type}_employees_button')],

    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup

def pass_by_docs(text=None) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text or "Пропустить этот шаг", callback_data=f'pass_by_docs')],

    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup


def actions_page_main_markup() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton('Главное меню')],
    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    return markup


def actions_back() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton('Главное меню'), KeyboardButton('Назад')],
    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    return markup


def absence_markup(excuses):

    keyboard = [
        [
            InlineKeyboardButton(excuse.name, callback_data=f'absence_excuse_{excuse.id}')
        ] for excuse in excuses
    ]

    markup = InlineKeyboardMarkup(keyboard)
    return markup
