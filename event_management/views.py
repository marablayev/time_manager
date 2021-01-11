from django.shortcuts import render

from rest_framework import viewsets

from .models import Event, EventConfirmation
from .serializers import EventSerializer, EventConfirmationSerializer


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventConfirmationModelViewSet(viewsets.ModelViewSet):
    queryset = EventConfirmation.objects.all()
    serializer_class = EventConfirmationSerializer
    http_method_names = ["get"]
