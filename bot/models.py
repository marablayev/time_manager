import pyotp

from django.db import models, transaction
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import PhoneNumber

from core.models import TimestampMixin
from .managers import OTPQueryset


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


class OTP(TimestampMixin):
    code = models.CharField("OTP", max_length=12, db_index=True, editable=False)
    verified = models.BooleanField("Подтверждён", default=False, editable=False)
    phone = PhoneNumberField("Мобильный телефон", editable=False)

    objects = OTPQueryset.as_manager()

    class Meta:
        verbose_name = "Одноразовый пароль"
        verbose_name_plural = "Одноразовые пароли"
        unique_together = ("code", "phone")

    @classmethod
    def generate(cls, phone: PhoneNumber):
        with transaction.atomic():
            instance = cls()
            instance.save()
            hotp = pyotp.HOTP(settings.HOTP_KEY, digits=settings.OTP_LENGTH)
            code = hotp.at(instance.pk)
            instance.code = code
            instance.phone = phone
            instance.save()
        return code
