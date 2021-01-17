from rest_framework import serializers

from time_management.utils import get_stats
from .models import Employee, Company


class EmployeeSerializer(serializers.ModelSerializer):
    time_stats = serializers.SerializerMethodField()
    company = serializers.CharField(source="company.name")

    class Meta:
        model = Employee
        fields = ("id", "role", "full_name", "chat_id", "phone", "birthday",
                  "bio", "company", "photo", "photo_card", "time_stats", "occupation")
        read_only_fields = ("photo", "photo_card")

    def get_time_stats(self, obj):
        stats = get_stats([obj])
        return stats[0]


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
