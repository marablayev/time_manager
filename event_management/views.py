import dateutil.parser

from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Event, EventConfirmation
from .serializers import EventSerializer, EventConfirmationSerializer


class EventModelViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.filter(date_time__date__gte=timezone.localdate())
    serializer_class = EventSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(employee=self.request.user)
        return queryset

    @action(methods=['GET'], detail=False)
    def for_user(self, request, *args, **kwargs):
        events = Event.objects.filter(confirmations__employee=request.user)
        return Response(self.get_serializer_class()(events, many=True).data)


class EventConfirmationModelViewSet(viewsets.ModelViewSet):
    queryset = EventConfirmation.objects.filter(event__date_time__date__gte=timezone.localdate())
    serializer_class = EventConfirmationSerializer
    http_method_names = ["get"]
