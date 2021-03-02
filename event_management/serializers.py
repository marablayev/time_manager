from django.core.files.base import ContentFile

from rest_framework import serializers

from employees.models import Employee
from .models import Event, EventConfirmation, EventDocs


class EventDocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDocs
        fields = ('id', 'file')


class EventSerializer(serializers.ModelSerializer):
    removed_docs = serializers.CharField(write_only=True, required=False, allow_null=True)
    new_docs = serializers.FileField(write_only=True, required=False, allow_null=True)
    removed_image = serializers.BooleanField(write_only=True)
    employee_name = serializers.CharField(source="employee.full_name", allow_null=True, required=False)
    all_employees = serializers.BooleanField(default=False, required=False)
    employee_names = serializers.SerializerMethodField()
    docs = serializers.SerializerMethodField()
    employee = serializers.PrimaryKeyRelatedField(required=False, allow_null=True, queryset=Employee.objects.all())

    class Meta:
        model = Event
        fields = ('id', 'all_employees', 'date_time', 'employee', 'notes',
                  'place', 'title', 'employees_to_notify',
                  'employee_name', 'image', 'employee_names', 'docs',
                  'removed_docs', 'new_docs', 'removed_image')

    def get_docs(self, obj):
        serializer = EventDocsSerializer(obj.docs.all(), many=True, context=self.context)
        return serializer.data

    def get_employee_names(self, obj):
        employees = Employee.objects.all()
        if not obj.all_employees:
            employees = obj.employees_to_notify.all()

        return list(employees.values_list('full_name', flat=True))


    def create(self, validated_data):
        doc = validated_data.pop('new_docs', None)
        user = self.context['request'].user
        validated_data.pop('removed_image', False)
        validated_data['employee'] = user
        instance = super(EventSerializer, self).create(validated_data)
        instance.save()
        if doc:
            EventDocs.objects.create(file=doc, event=instance)
        return instance

    def update(self, instance, validated_data):
        doc = validated_data.pop('new_docs', None)
        if validated_data.pop('removed_image', False):
            validated_data['image'] = None
        if validated_data.pop('removed_docs', False):
            EventDocs.objects.filter(event=instance).delete()

        instance = super(EventSerializer, self).update(instance, validated_data)
        if doc:
            EventDocs.objects.filter(event=instance).delete()
            EventDocs.objects.create(file=doc, event=instance)

        return instance


class EventConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventConfirmation
        fields = "__all__"
