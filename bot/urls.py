from django.urls import path

from . import views


urlpatterns = [
    path('webhook/client/<str:token>/', views.ClientBotWebHookView.as_view(),
         name='client'),
]
