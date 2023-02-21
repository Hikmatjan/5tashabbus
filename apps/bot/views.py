import json
import os
from queue import Queue

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram import Bot, Update
from telegram.ext import CommandHandler, ConversationHandler, Dispatcher, PicklePersistence, CallbackQueryHandler

from apps.bot.states import state
from apps.bot.telegrambot import start, check_join_channel
from core.settings.base import BOT_TOKEN as token
from django.conf import settings


def setup(token):
    bot = Bot(token=token)
    queue = Queue()
    # create the dispatcher
    if not os.path.exists(os.path.join(settings.BASE_DIR, "apps", "bot", "state_record")):
        os.makedirs(os.path.join(settings.BASE_DIR, "apps", "bot", "state_record"))
    dp = Dispatcher(bot, queue, workers=4, use_context=True, persistence=PicklePersistence(
        filename=os.path.join(
            settings.BASE_DIR, "apps", "bot", "state_record", "conversationbot"
        )
    ),  # to store member state
                    )

    states = {
        state.JOIN_CHANNELS: [
            CallbackQueryHandler(check_join_channel)
        ]
    }
    entry_points = [CommandHandler('start', start)]
    fallbacks = [CommandHandler('start', start)]
    conversation_handler = ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=fallbacks,
        persistent=True,
        name="conversationbot",
    )
    dp.add_handler(conversation_handler)
    return dp


class HandleWebhook(APIView):
    def get(self, request):
        bot = Bot(token=token)
        # set webhook
        webhook_url = settings.WEBHOOK_URL
        if webhook_url:
            bot.set_webhook(webhook_url + '/bot/webhook/')
        print(bot.bot, bot.username, bot.first_name, bot.request)
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        bot = Bot(token=token)
        update = Update.de_json(json.loads(request.body.decode('utf-8')), bot)
        dp = setup(token)
        dp.process_update(update)
        return Response(status=status.HTTP_200_OK)
