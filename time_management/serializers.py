from rest_framework import serializers

from .models import EmployeeActivity, Holiday


class EmployeeActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeActivity
        fields = "__all__"


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = "__all__"
