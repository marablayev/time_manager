from django.shortcuts import render
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import News
from .serializers import NewsSerializer


class NewsModelViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(methods=['GET'], detail=False)
    def for_user(self, request, *args, **kwargs):
        user = request.user
        employee = user.employee_profile
        news = News.objects.filter(Q(employees_to_notify=employee) | Q(all_employees=True)).distinct()
        return Response(self.get_serializer_class()(news, many=True).data)
