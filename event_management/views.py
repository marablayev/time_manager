from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response

from .models import Event, EventConfirmation
from .serializers import EventSerializer, EventConfirmationSerializer


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        data['employee'] = user.employee_profile.id
        serializer = EventSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        return Response(EventSerializer(event, context={'request': request}).data)


class EventConfirmationModelViewSet(viewsets.ModelViewSet):
    queryset = EventConfirmation.objects.all()
    serializer_class = EventConfirmationSerializer
    http_method_names = ["get"]
