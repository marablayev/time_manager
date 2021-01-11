from rest_framework import serializers

from .models import Task, TaskConfirmation


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskConfirmation
        fields = "__all__"
