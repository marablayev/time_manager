from rest_framework import viewsets

from .models import Task, TaskConfirmation
from .serializers import TaskSerializer, TaskConfirmationSerializer


class TaskModelViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskConfirmationModelViewSet(viewsets.ModelViewSet):
    queryset = TaskConfirmation.objects.all()
    serializer_class = TaskConfirmationSerializer
    http_method_names = ["get"]
