import hashlib
import hmac

from django.conf import settings

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

from employees.models import Employee


class TelegramLoginSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    auth_date = serializers.CharField(required=False)
    hash = serializers.CharField()


    def validate(self, attrs):
        hash = attrs.pop('hash')
        keys = list(attrs.keys())
        keys.sort()

        data_check_string = '/n'.join([f'{key}={attrs[key]}' for key in keys])
        secret_key = hashlib.sha256(settings.BOT_TOKEN.encode('utf-8')).digest()

        hmac_secret = hmac.new(secret_key, msg=data_check_string.encode('utf-8'), digestmod=hashlib.sha256)

        employee = Employee.objects.filter(chat_id=int(attrs['id'])).first()
        if employee:
            refresh = BaseTokenObtainPairSerializer.get_token(employee.user)
            data = {"refresh": str(refresh), "access": str(refresh.access_token)}
            return data
            
        return attrs
