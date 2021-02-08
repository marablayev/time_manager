from django.conf import settings

from rest_framework import views, status, permissions
from rest_framework.response import Response
from telegram import Update

from bot.bot import bot_init
from .serializers import TelegramLoginSerializer


class ClientBotWebHookView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        token = kwargs.get("token")
        updater = bot_init(token)
        update = Update.de_json(request.data, updater.bot)
        updater.dispatcher.process_update(update)
        return Response(status=status.HTTP_200_OK)


class TelegramLoginView(views.APIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = TelegramLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = TelegramLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
