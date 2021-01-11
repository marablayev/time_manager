from django.db import models


class TelegramReplyTemplate(models.Model):
    """
    Model to store Telegram bot replies templates
    """
    code = models.CharField("Код сообщения", max_length=255, unique=True)
    message = models.TextField("Сообщение")

    class Meta:
        verbose_name = 'Шаблон ответа в Телеграм боте'
        verbose_name_plural = 'Шаблоны ответа в Телеграм боте'

    def __str__(self):
        return self.code

    @classmethod
    def get_message(cls, code):
        reply = cls.objects.filter(code=code).first()
        return reply.message if reply else 'Ошибка шаблона.'
