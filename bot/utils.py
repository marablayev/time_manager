from django.conf import settings

from bot.bot import bot_init
from .models import OTP


def send_otp(employee):
    otp = OTP.generate(employee.phone.as_e164)

    try:
        updater = bot_init(settings.BOT_TOKEN)
        updater.send_otp(otp, employee.chat_id)
    except Exception as e:
        return False

    return True


def verify_otp(code, phone):
    try:
        otp = OTP.objects.active().get(code=code, phone=phone)
    except OTP.DoesNotExist:
        return False
    otp.verified = True
    otp.save(update_fields=["verified"])
    return True
