from rest_framework import viewsets

from .models import EmployeeActivity, Holiday
from .serializers import EmployeeActivitySerializer, HolidaySerializer


class EmployeeActivityModelViewSet(viewsets.ModelViewSet):
    queryset = EmployeeActivity.objects.all()
    serializer_class = EmployeeActivitySerializer
    http_method_names = ["get", "put", "patch"]


class HolidayModelViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
