import os
import inspect
from dateutil import parser as dt_parser
from urllib.parse import urlparse
from threading import Thread

from django.utils import timezone

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from employees.models import Employee

from ..markups import get_markup



def get_file_path(path):
    parsed = urlparse(path)
    return f"media/{os.path.basename(parsed.path)}"


class ActionsHandler:

    def get_actions_handlers(self):
        return [
            CommandHandler('start', self.start),
            MessageHandler(Filters.regex(f'^Главное меню$'), self.start),
            MessageHandler(Filters.regex(f'^Назад$'), self.actions_page),
            MessageHandler(Filters.regex(f"^inline_employee_selected_(-?[0-9]+)$"), self.add_employee_to_list),
            CallbackQueryHandler(self.model_selected, pattern='^(event|task|news)_create_selected$'),
        ]

    def get_event_creation_handlers(self):
        return self.get_actions_handlers() + [
            CallbackQueryHandler(self.pass_by_image_event, pattern='^pass_by_image$'),
            CallbackQueryHandler(self.pass_by_docs_event, pattern='^pass_by_docs$'),
            CallbackQueryHandler(self.all_employees_button, pattern='^(all|finish)_employees_button$'),
            MessageHandler(Filters.photo, self.handle_image_docs),
            MessageHandler(Filters.document, self.handle_image_docs),
            MessageHandler(Filters.text, self.handle_text),
        ]

    def get_task_creation_handlers(self):
        return self.get_actions_handlers() + [
            MessageHandler(Filters.text, self.handle_text),
        ]

    def get_news_creation_handlers(self):
        return self.get_actions_handlers() + [
            MessageHandler(Filters.text, self.handle_text),
        ]

    def actions_page(self, update, context, text=None):
        if update.callback_query:
            query = update.callback_query
            query.answer()
            chat = query.message.chat
        else:
            chat = update.message.chat

        self.bot.send_message(chat.id, text=text or 'Создание', reply_markup=get_markup('actions_page_main_markup'))

        text = "Пожалуйста, выберите тип объекта для создания: "
        markup = get_markup('actions_page_markup')

        if update and update.callback_query:
            self.bot.delete_message(chat.id, query.message.message_id)
            self.bot.send_message(chat.id, text, reply_markup=markup, parse_mode='HTML')
        elif update:
            update.message.reply_text(text=text, reply_markup=markup, parse_mode='HTML')

        return self.ACTIONS_PAGE

    def model_selected(self, update, context):
        query = update.callback_query
        query.answer()
        chat = query.message.chat
        type, *args = query.data.split("_")

        context.user_data['temp_action_creation'] = {
            'type': type
        }
        title_name = "задачи"
        state = self.TASK_CREATE
        if type == 'news':
            title_name = 'новости'
            state = self.NEWS_CREATE
        elif type == 'event':
            title_name = 'событии'
            state = self.EVENT_CREATE

        text = f"Пожалуйста, введите заголовок {title_name}"
        markup = get_markup('actions_back')
        self.bot.delete_message(chat.id, query.message.message_id)
        self.bot.send_message(chat.id, text, reply_markup=markup, parse_mode='HTML')

        return state

    def handle_text(self, update, context):
        temp_action_creation = context.user_data['temp_action_creation']
        type = temp_action_creation['type']

        if type == 'event':
            return self.event_handle_text(update, context)
        if type == 'task':
            return self.event_handle_text(update, context)
        if type == 'news':
            return self.event_handle_text(update, context)

    def pass_by_docs_event(self, update, context):
        query = update.callback_query
        query.answer()
        text = 'Чтобы найти пользователей: \n\n'
        text += ' - Наберите название данного бота(@dev_time_manager_bot) и нажмите на пробел\n'
        text += ' - После начните набирать ФИО вашего коллеги\n'
        text += ' - Выберите из списка'
        temp_action_creation = context.user_data['temp_action_creation']
        ids = temp_action_creation.get('employee_ids', [])
        if Employee.objects.filter(id__in=ids).exists():
            employees = Employee.objects.filter(id__in=ids)
            names = list(employees.values_list("full_name", flat=True))
            text += f'\nПриглашены: \n{", ".join(names)}'

        reply_markup = get_markup('all_employees_markup')
        query.edit_message_text(text, reply_markup=reply_markup)

    def handle_image_docs(self, update, context):
        image = update.message.photo
        document = update.message.document

        temp_action_creation = context.user_data['temp_action_creation']
        if temp_action_creation.get('image') is None and not image:
            update.message.reply_text('Закрепите картинку в правильном формате', reply_markup=get_markup('pass_by_image'))
            return
        elif temp_action_creation.get('image') is None:
            temp_action_creation['image'] = image[-1].file_id
            text = 'Закрепите Документы если они есть. Если нет, нажмите на кнопку Пропустить данный шаг.'
            reply_markup = get_markup('pass_by_docs')
            update.message.reply_text(text, reply_markup=reply_markup)
            return

        if document:
            temp_action_creation.setdefault('docs', [])
            temp_action_creation['docs'].append(document.file_id)
            text = 'Закрепите еще Документы, либо нажмите на кнопку Продолжить.'
            reply_markup = get_markup('pass_by_docs', 'Продолжить')
            update.message.reply_text(text, reply_markup=reply_markup)
            return

    def all_employees_button(self, update, context):
        from event_management.models import Event, EventDocs
        query = update.callback_query
        chat = query.message.chat
        query.answer()
        type, *args = query.data.split("_")

        temp_action_creation = context.user_data['temp_action_creation']
        if type == 'all':
            temp_action_creation['all_employees'] = True

        image = None
        docs = []
        employee = Employee.objects.filter(chat_id=chat.id).first()
        to_notify = temp_action_creation.pop('employee_ids', [])
        date_time = temp_action_creation.pop('date_time', [])
        date_time = dt_parser.parse(date_time)
        # try:
        #     date
        object_type = temp_action_creation.pop('type', '')
        if temp_action_creation.get('image'):
            image = self.bot.getFile(temp_action_creation.pop('image'))
            image = image.download(get_file_path(image.file_path))

        if temp_action_creation.get('docs'):
            docs = [self.bot.getFile(file_id) for file_id in temp_action_creation.pop('docs')]
            docs = [f.download(get_file_path(f.file_path)) for f in docs]

        if object_type == 'event':
            event = Event(employee=employee, **temp_action_creation)
            event.image = os.path.basename(image) if image else image
            event.date_time = date_time
            event.save()
            event.employees_to_notify.set(to_notify)
            for doc in docs:
                EventDocs.objects.create(event=event, file=os.path.basename(doc))
            event.save()

        context.user_data['temp_action_creation'] = {}
        text = 'Ваше событие создано.'
        return self.actions_page(update, context, text)

    def event_handle_text(self, update, context):
        temp_action_creation = context.user_data['temp_action_creation']
        text = 'Введите описание события'

        kwargs = {}

        if not temp_action_creation.get('title'):
            temp_action_creation['title'] = update.message.text
        elif not temp_action_creation.get('notes'):
            temp_action_creation['notes'] = update.message.text
            text = 'Введите место проведения события'
        elif not temp_action_creation.get('place'):
            temp_action_creation['place'] = update.message.text
            text = 'Введите дату и время события. Пример: 2021-01-25 10:00'
        elif not temp_action_creation.get('date_time'):
            try:
                date = dt_parser.parse(update.message.text)
                temp_action_creation['date_time'] = update.message.text
                text = 'Закрепите картинку если она есть. Если нет нажмите на кнопку Пропустить данный шаг.'
                kwargs['reply_markup'] = get_markup('pass_by_image')
            except:
                text = 'Введите дату в правильном формате. Пример: 2021-01-25 10:00'
        else:
            text = 'Следуйте инструкции'

        context.user_data['temp_action_creation'] = temp_action_creation
        update.message.reply_text(text, **kwargs)

    def pass_by_image_event(self, update, context):
        query = update.callback_query
        query.answer()
        temp_action_creation = context.user_data['temp_action_creation']
        temp_action_creation['image'] = ''

        text = 'Закрепите Документы если они есть. Если нет, нажмите на кнопку Пропустить данный шаг.'
        reply_markup = get_markup('pass_by_docs')
        query.edit_message_text(text, reply_markup=reply_markup)

    def add_employee_to_list(self, update, context):
        chat = update.message.chat
        *args, employee_id = update.message.text.split("_")
        self.bot.delete_message(chat.id, update.message.message_id)
        to_delete = context.user_data.get('to_delete_messages')
        if to_delete:
            for id in to_delete:
                try:
                    self.bot.delete_message(chat.id, id)
                except:
                    continue

        temp_action_creation = context.user_data['temp_action_creation']
        temp_action_creation.setdefault('employee_ids', [])
        ids = temp_action_creation['employee_ids']
        ids.append(employee_id)

        context.user_data['temp_action_creation']['employee_ids'] = ids
        text = f'Чтобы закончить создание события, нажмите на кнопку Закончить'
        temp_action_creation = context.user_data['temp_action_creation']
        ids = temp_action_creation.get('employee_ids', [])
        if Employee.objects.filter(id__in=ids).exists():
            employees = Employee.objects.filter(id__in=ids).distinct()
            names = list(employees.values_list("full_name", flat=True))
            text += f'\nПриглашены: \n{", ".join(names)}'

        reply_markup = get_markup('all_employees_markup', 'finish')
        msg = update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.setdefault('to_delete_messages', [])
        context.user_data['to_delete_messages'].append(msg.message_id)
