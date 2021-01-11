from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EmployeeActivityModelViewSet, HolidayModelViewSet


router = DefaultRouter()
router.register("", EmployeeActivityModelViewSet)
router.register("holidays", HolidayModelViewSet)

urlpatterns = [
    path("", include(router.urls))
]
