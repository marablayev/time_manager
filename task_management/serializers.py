from rest_framework import serializers

from .models import Task, TaskConfirmation


class TaskSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", allow_null=True, required=False)
    all_employees = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Task
        fields = ('id', 'all_employees', 'due_time', 'employee', 'text',
                  'name', 'employees_to_notify',
                  'employee_name', 'image')

    def create(self, validated_data):
        instance = super(TaskSerializer, self).create(validated_data)
        instance.save()
        return instance


class TaskConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfirmation
        fields = "__all__"
