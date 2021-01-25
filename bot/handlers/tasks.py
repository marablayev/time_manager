from threading import Thread

from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, ReplyKeyboardRemove, error as TelegramError, BotCommand)
from telegram.ext import (
    Updater, CommandHandler, Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, PicklePersistence)

from employees.models import Employee

from ..markups import get_markup

class TasksHandler:

    def task_notify(self, task, employees):
        bot = self.bot
        image = task.image
        message = f"{task.name}\n\n{task.text}"
        if task.employee:
            message += f"\n<b>От: </b>{task.employee.full_name}"

        if task.due_time:
            message += f"\n<b>Дэдлайн: </b>{task.due_time.strftime('%Y-%m-%d %H:%M')}"

        for employee in employees:
            args = tuple()
            kwargs = {'parse_mode': 'HTML', 'reply_markup': get_markup('task_notify_markup', task.id)}
            if image:
                method = bot.send_photo
                args = (employee.chat_id, image)
                kwargs['caption'] = message
            else:
                method = bot.send_message
                args = (employee.chat_id, message)
            f_msg = self.reply_manager.get_message('tasks_received_reply')
            thread = Thread(target=bot.send_message, args=(employee.chat_id, f_msg))
            thread.start()
            thread = Thread(target=method, args=args, kwargs=kwargs)
            thread.start()

    def task_done(self, update, context):
        from task_management.models import TaskConfirmation
        query = update.callback_query
        query.answer()
        chat = query.message.chat
        *args, task_id = query.data.split('_')

        employee = Employee.objects.filter(chat_id=chat.id).first()
        task_conf = TaskConfirmation.objects.filter(employee=employee, task_id=task_id).first()
        if task_conf:
            task_conf.done = True
            task_conf.save()

        query.edit_message_text(self.reply_manager.get_message('task_done_reply'))
