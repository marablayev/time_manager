from rest_framework import serializers

from employees.models import Employee
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", allow_null=True, required=False)
    removed_image = serializers.BooleanField(write_only=True, required=False)
    all_employees = serializers.BooleanField(default=False, required=False)
    employee = serializers.PrimaryKeyRelatedField(required=False, allow_null=True, queryset=Employee.objects.all())

    class Meta:
        model = News
        fields = ('id', 'all_employees', 'date_time', 'employee', 'text',
                  'title', 'employees_to_notify',
                  'employee_name', 'image', 'removed_image')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['employee'] = user

        instance = super(NewsSerializer, self).create(validated_data)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if validated_data.pop('removed_image', False):
            validated_data['image'] = None

        instance = super(NewsSerializer, self).update(instance, validated_data)
        return instance
