from rest_framework import serializers
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)
from phonenumber_field.serializerfields import PhoneNumberField


from bot.models import OTP
from bot.utils import verify_otp, send_otp
from time_management.utils import get_stats
from time_management.models import Vacation
from .models import Employee, Company


class EmployeeSerializer(serializers.ModelSerializer):
    time_stats = serializers.SerializerMethodField()
    company = serializers.CharField(source="company.name")

    class Meta:
        model = Employee
        fields = ("id", "role", "full_name", "chat_id", "phone", "birthday",
                  "bio", "company", "photo", "photo_card", "time_stats",
                  "occupation", "role")
        read_only_fields = ("photo", "photo_card")

    def get_time_stats(self, obj):
        stats = get_stats([obj])
        return stats[0]


class VacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacation
        fields = ('__all__')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class EmployeePhotoUploadSerializer(serializers.ModelSerializer):
    photo = serializers.FileField(allow_null=True, required=False)
    photo_card = serializers.FileField(allow_null=True, required=False)

    class Meta:
        model = Employee
        fields = ('id', 'photo', 'photo_card')


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["code"] = serializers.CharField()
        self.fields.pop("password")
        self.employee: Employee = None

    def validate(self, attrs):
        phone = attrs[self.username_field]
        code = attrs["code"]

        employee = Employee.objects.filter(phone=phone)

        if not employee.exists():
            raise serializers.ValidationError(
                {"detail": "Пользователь не существует"}
            )

        if verify_otp(code=code, phone=phone):
            self.employee = employee.first()
        else:
            raise serializers.ValidationError({"code": "Не правильный код. Попробуйте снова."})

        if self.employee is None or not self.employee.is_active:
            raise serializers.ValidationError(
                {'detail': "Данный пользователь не активен."}
            )

        refresh = self.get_token(self.employee)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "phone": self.employee.phone.as_e164,
            "full_name": self.employee.full_name
        }

        return data


class PhoneValidateSerializer(serializers.Serializer):
    phone = PhoneNumberField(required=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        instance = Employee.objects.filter(phone=phone).first()

        if not instance:
            raise serializers.ValidationError(
                {"phone": "Сотрудник с таким телефоном не существует"})

        if OTP.objects.timeout().filter(phone=phone):
            raise serializers.ValidationError(
                {"detail": "Код отправлен. Попробуйте переотправить немного позже."})

        sent = send_otp(instance)
        if not sent:
            raise serializers.ValidationError(
                {"detail": "Код не отправлен. Ошибка при отправке."})
        return attrs
