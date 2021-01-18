import inspect

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

    def actions_page(self, update, context):
        pass

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

        text = f"{event.title} {event.employee.full_name}"
        self.bot.send_message(
            chat_id, text=text, reply_markup=markup, parse_mode='HTML')


    def offers_page(self, update, context):
        client = TelegramClient.objects.get(chat_id=update.message.chat.id)
        offers = BankOffer.objects.filter(
            partner=client.partner, status__in=BankOfferStatuses.telegram_statuses())
        if not offers.exists():
            msg = update.message.reply_text(
                self.reply_manager.get_message('no_offers_reply'), parse_mode='HTML',)
            self.add_message_to_history(context, msg)
            return

        self.render_offer(update.message.chat.id, context, offers)
        return self.OFFERS_STATE

    def get_offer_text(self, offer):
        data = {
            "html_template": offer.program.html_template or '',
            "min_amount": int(offer.program.min_amount) if offer.program.min_amount else '',
            "max_amount": int(offer.program.max_amount) if offer.program.max_amount else '',
            "min_period": int(offer.program.min_period) if offer.program.min_period else '',
            "max_period": int(offer.program.max_period) if offer.program.max_period else '',
            "comission": int(offer.program.comission) if offer.program.comission else '',
            "interest": int(offer.program.interest) if offer.program.interest else '',
            "status": offer.get_status_display() + EMOJIS.get(offer.status, ''),
        }
        return self.OFFER_TEMPLATE.format(**data)

    def render_offer(self, chat_id, context, offers, index=0):
        # Method gets image and creates caption for news item reply message.
        offer = offers[index]
        max_index = offers.count() - 1
        context.user_data['latest_offers_index'] = index
        image = offer.program.image
        is_waiting = offer.status == BankOfferStatuses.WAITING
        markup = markups.get_offer_markup(index, max_index, offer.id, is_waiting)

        caption = self.get_offer_text(offer)
        if image:
            msg = self.bot.send_photo(
                chat_id, photo=image, caption=caption,
                reply_markup=markup, parse_mode='HTML')
        else:
            msg = self.bot.send_message(
                chat_id, text=caption, reply_markup=markup, parse_mode='HTML')

        self.add_message_to_history(context, msg)

    def offer_get(self, update, context):
        query = update.callback_query
        query.answer()
        *args, index = query.data.split('_')
        index = int(index)

        client = TelegramClient.objects.get(chat_id=query.message.chat.id)
        offers = BankOffer.objects.filter(partner=client.partner)
        if offers.count() > 1:
            self.bot.delete_message(query.message.chat.id, query.message.message_id)
            self.render_offer(query.message.chat.id, context, offers, index)
