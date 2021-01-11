from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EventModelViewSet, EventConfirmationModelViewSet


router = DefaultRouter()
router.register("", EventModelViewSet)
router.register("confirmations", EventConfirmationModelViewSet)

urlpatterns = [
    path("", include(router.urls))
]
