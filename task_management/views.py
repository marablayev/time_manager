from django.db.models import Q

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Task, TaskConfirmation
from .serializers import TaskSerializer, TaskConfirmationSerializer


class TaskModelViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        data['employee'] = user.employee_profile.id
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(self.get_serializer_class()(task).data)

    @action(methods=['GET'], detail=False)
    def for_user(self, request, *args, **kwargs):
        user = request.user
        employee = user.employee_profile
        tasks = Task.objects.filter(confirmations__employee=employee)
        return Response(self.get_serializer_class()(tasks, many=True).data)


class TaskConfirmationModelViewSet(viewsets.ModelViewSet):
    queryset = TaskConfirmation.objects.all()
    serializer_class = TaskConfirmationSerializer
    http_method_names = ["get"]
