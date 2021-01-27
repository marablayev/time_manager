from rest_framework import serializers

from .models import Task, TaskConfirmation


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

    def create(self, validated_data):
        instance = super(TaskSerializer, self).create(validated_data)
        instance.save()
        return instance


class TaskConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfirmation
        fields = "__all__"
