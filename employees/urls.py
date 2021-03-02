from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EmployeeModelViewSet, CompanyModelViewSet, EmployeePhotoUploadView,
    TokenObtainPairView, SendOTPView,)


router = DefaultRouter()
router.register("companies", CompanyModelViewSet)
router.register("", EmployeeModelViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("upload/<int:pk>/", EmployeePhotoUploadView.as_view()),
    path("otp/send/", SendOTPView.as_view()),
    path("otp/verify/", TokenObtainPairView.as_view(), name="token_obtain"),
]
