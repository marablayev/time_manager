from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskModelViewSet, TaskConfirmationModelViewSet


router = DefaultRouter()
router.register("", TaskModelViewSet)
router.register("confirmations", TaskConfirmationModelViewSet)

urlpatterns = [
    path("", include(router.urls))
]
