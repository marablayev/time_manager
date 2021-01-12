import os
import json

from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders

from bot.models import TelegramReplyTemplate


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        file = open(finders.find('bot/replies_dump.json'), 'r')
        raw_data = file.read()
        data = json.loads(raw_data)
        for item in data:
            if not TelegramReplyTemplate.objects.filter(code=item['code']).exists():
                TelegramReplyTemplate.objects.create(**item)
