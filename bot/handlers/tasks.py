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

    def get_tasks_handlers(self):
        return self.get_profile_handlers() + [
            CallbackQueryHandler(self.task_get, pattern='^tasks_item_get_(-?[0-9]+)$'),
        ]

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

    def my_tasks(self, update, context):
        from task_management.models import Task
        if update.callback_query:
            query = update.callback_query
            query.answer()
            chat = query.message.chat
        else:
            chat = update.message.chat

        employee = Employee.objects.filter(chat_id=chat.id).first()
        tasks = Task.objects.filter(confirmations__employee=employee)
        if not tasks.exists():
            msg = update.message.reply_text(
                self.reply_manager.get_message('no_tasks_reply'), parse_mode='HTML',)
            return

        self.render_task(chat.id, context, tasks)
        return self.TASKS_PAGE

    def render_task(self, chat_id, context, tasks, index=0):
        task = tasks[index]
        max_index = tasks.count() - 1
        context.user_data['latest_tasks_index'] = index
        markup = get_markup('get_task_markup', index, max_index, task.id)

        image = task.image
        message = f"{task.name}\n\n{task.text}"
        if task.employee:
            message += f"\n<b>Владелец: </b>{task.employee.full_name}"

        if task.due_time:
            message += f"\n<b>Дэдлайн: </b>{task.due_time.strftime('%Y-%m-%d %H:%M')}"

        if image:
            msg = self.bot.send_photo(
                chat_id, photo=image, caption=message,
                reply_markup=markup, parse_mode='HTML')
        else:
            msg = self.bot.send_message(
                chat_id, text=message, reply_markup=markup, parse_mode='HTML')


    def task_get(self, update, context):
        from task_management.models import Task
        query = update.callback_query
        query.answer()
        *args, index = query.data.split('_')
        index = int(index)

        employee = Employee.objects.filter(chat_id=query.message.chat.id).first()
        tasks = Task.objects.filter(confirmations__employee=employee, )
        if tasks.count() > 1:
            self.bot.delete_message(query.message.chat.id, query.message.message_id)
            self.render_task(query.message.chat.id, context, tasks, index)
