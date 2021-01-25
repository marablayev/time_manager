import inspect
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


class EventsHandler:

    def get_event_handlers(self):
        return self.get_profile_handlers() + [
            CallbackQueryHandler(self.event_get, pattern='^events_item_get_(-?[0-9]+)$'),
        ]

    def event_notify(self, event, employees):
        bot = self.bot
        image = event.image
        message = f"{event.title}\n\n{event.notes}"
        if event.employee:
            message += f"\n<b>Владелец: </b>{event.employee.full_name}"

        if event.place:
            message += f"\n<b>Местоположение: </b>{event.place}"

        if event.date_time:
            message += f"\n<b>Дата и время: </b>{event.date_time.strftime('%Y-%m-%d %H:%M')}"

        for employee in employees:
            args = tuple()
            kwargs = {'parse_mode': 'HTML', 'reply_markup': get_markup('event_notify_markup', event.id)}
            if image:
                method = bot.send_photo
                args = (employee.chat_id, image)
                kwargs['caption'] = message
            else:
                method = bot.send_message
                args = (employee.chat_id, message)
            f_msg = self.reply_manager.get_message('events_received_reply')
            thread = Thread(target=bot.send_message, args=(employee.chat_id, f_msg))
            thread.start()
            thread = Thread(target=method, args=args, kwargs=kwargs)
            thread.start()

    def set_event_confirmation(self, update, context, is_accepted=False):
        from event_management.models import EventConfirmation
        query = update.callback_query
        query.answer()
        chat = query.message.chat
        *args, event_id = query.data.split('_')

        employee = Employee.objects.filter(chat_id=chat.id).first()
        event_conf = EventConfirmation.objects.filter(employee=employee, event_id=event_id).first()
        if event_conf:
            event_conf.accepted = is_accepted
            event_conf.save()

        return query

    def event_accepted(self, update, context):
        query = self.set_event_confirmation(update, context, True)
        self.bot.delete_message(query.message.chat_id, query.message.message_id)
        self.bot.send_message(query.message.chat_id, text=self.reply_manager.get_message('event_accepted_reply'))

    def event_rejected(self, update, context):
        query = self.set_event_confirmation(update, context, False)
        self.bot.delete_message(query.message.chat_id, query.message.message_id)
        self.bot.send_message(query.message.chat_id, text=self.reply_manager.get_message('event_rejected_reply'))


    def my_events(self, update, context):
        from event_management.models import Event
        if update.callback_query:
            query = update.callback_query
            query.answer()
            chat = query.message.chat
        else:
            chat = update.message.chat

        employee = Employee.objects.filter(chat_id=chat.id).first()
        current = timezone.now()
        events = Event.objects.filter(confirmations__employee=employee, date_time__gte=current)
        if not events.exists():
            msg = update.message.reply_text(
                self.reply_manager.get_message('no_events_reply'), parse_mode='HTML',)
            return

        self.render_event(chat.id, context, events)
        return self.EVENTS_PAGE

    def render_event(self, chat_id, context, events, index=0):
        event = events[index]
        max_index = events.count() - 1
        context.user_data['latest_events_index'] = index
        markup = get_markup('get_event_markup', index, max_index, event.id)

        image = event.image
        message = f"{event.title}\n\n{event.notes}"
        if event.employee:
            message += f"\n<b>Владелец: </b>{event.employee.full_name}"

        if event.place:
            message += f"\n<b>Местоположение: </b>{event.place}"

        if event.date_time:
            message += f"\n<b>Дата и время: </b>{event.date_time.strftime('%Y-%m-%d %H:%M')}"

        if image:
            msg = self.bot.send_photo(
                chat_id, photo=image, caption=message,
                reply_markup=markup, parse_mode='HTML')
        else:
            msg = self.bot.send_message(
                chat_id, text=message, reply_markup=markup, parse_mode='HTML')


    def event_get(self, update, context):
        from event_management.models import Event
        query = update.callback_query
        query.answer()
        *args, index = query.data.split('_')
        index = int(index)

        employee = Employee.objects.filter(chat_id=query.message.chat.id).first()
        current = timezone.now()
        events = Event.objects.filter(confirmations__employee=employee, date_time__gte=current)
        if events.count() > 1:
            self.bot.delete_message(query.message.chat.id, query.message.message_id)
            self.render_event(query.message.chat.id, context, events, index)
