from rest_framework import serializers

from .models import Employee, Company


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "role", "full_name", "chat_id", "phone", "birthday",
                  "bio", "company", "photo", "photo_card")
        read_only_fields = ("photo", "photo_card")


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
