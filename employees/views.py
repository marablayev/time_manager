from rest_framework import viewsets

from .models import Employee, Company
from .serializers import EmployeeSerializer, CompanySerializer


class EmployeeModelViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class CompanyModelViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
