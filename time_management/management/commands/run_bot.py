from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from bot.bot import bot_init

class Command(BaseCommand):
    help = 'Runbot'

    def handle(self, *args, **options):
        updater = bot_init(settings.BOT_TOKEN)
        updater.start_polling()
        updater.idle()
