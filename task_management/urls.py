from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskModelViewSet, TaskConfirmationModelViewSet


router = DefaultRouter()
router.register("confirmations", TaskConfirmationModelViewSet)
router.register("", TaskModelViewSet)

urlpatterns = [
    path("", include(router.urls))
]
