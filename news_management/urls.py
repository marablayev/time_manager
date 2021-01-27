from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import NewsModelViewSet


router = DefaultRouter()
router.register("", NewsModelViewSet)

urlpatterns = [
    path("", include(router.urls))
]
