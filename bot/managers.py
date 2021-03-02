from datetime import timedelta

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone


class OTPQueryset(QuerySet):
    def active(self):
        created_min = timezone.now() - timedelta(seconds=int(settings.OTP_VALIDITY_PERIOD))
        return self.filter(created_at__gte=created_min, verified=False)

    def timeout(self):
        created_min = timezone.now() - timedelta(seconds=int(settings.OTP_REPEAT_TIMEOUT))
        return self.filter(created_at__gte=created_min)
