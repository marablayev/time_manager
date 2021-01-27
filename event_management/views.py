from django.shortcuts import render
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Event, EventConfirmation
from .serializers import EventSerializer, EventConfirmationSerializer


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        data['employee'] = user.employee_profile.id
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        return Response(self.get_serializer_class()(event).data)

    @action(methods=['GET'], detail=False)
    def for_user(self, request, *args, **kwargs):
        user = request.user
        employee = user.employee_profile
        events = Event.objects.filter(confirmations__employee=employee)
        return Response(self.get_serializer_class()(events, many=True).data)


class EventConfirmationModelViewSet(viewsets.ModelViewSet):
    queryset = EventConfirmation.objects.all()
    serializer_class = EventConfirmationSerializer
    http_method_names = ["get"]
