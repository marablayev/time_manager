from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import get_object_or_404

from time_management.utils import write_to_xlxs
from .models import Employee, Company
from .serializers import EmployeeSerializer, CompanySerializer, EmployeePhotoUploadSerializer


class EmployeeModelViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(methods=["GET"], detail=False)
    def export(self, request, *args, **kwargs):
        return write_to_xlxs()


class EmployeePhotoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, pk=None, *args, **kwargs):
        obj = get_object_or_404(Employee, id=pk)
        context = {"request": request}
        serializer = EmployeePhotoUploadSerializer(
            obj,
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        resp_serializer = EmployeeSerializer(instance, context=context)
        return Response(resp_serializer.data, status=200)


class CompanyModelViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
