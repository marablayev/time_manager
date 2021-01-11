from rest_framework import serializers

from .models import Event, EventConfirmation


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventConfirmation
        fields = "__all__"
