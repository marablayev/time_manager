from rest_framework import serializers

from .models import Event, EventConfirmation


class EventSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", allow_null=True, required=False)
    all_employees = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Event
        fields = ('id', 'all_employees', 'date_time', 'employee', 'notes',
                  'place', 'title', 'employees_to_notify',
                  'employee_name')


class EventConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventConfirmation
        fields = "__all__"
