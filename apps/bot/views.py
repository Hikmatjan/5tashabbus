import json
import os
from queue import Queue

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from telegram import Bot, Update
from telegram.ext import CommandHandler, ConversationHandler, Dispatcher, PicklePersistence, CallbackQueryHandler, \
    MessageHandler, Filters

from apps.bot.states import state
from apps.bot.telegrambot import start, check_join_channel, get_region, get_tuman, get_product, main_menu, \
    about_us_button, add_product_to_savatcha, savatcha, get_phone_number, get_address, confirm_address
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
        ],
        state.CHOOSE_REGION: [
            CallbackQueryHandler(get_region)
        ],
        state.CHOOSE_TUMAN: [
            CallbackQueryHandler(get_tuman)
        ],
        state.CHOOSE_PRODUCT: [
            CallbackQueryHandler(get_product)
        ],
        state.MAIN_MENU: [
            CallbackQueryHandler(main_menu)
        ],
        state.ABOUT_US: [
            CallbackQueryHandler(about_us_button)
        ],
        state.BUY_PRODUCT: [
            CallbackQueryHandler(add_product_to_savatcha)
        ],
        state.SAVATCHA: [
            CallbackQueryHandler(savatcha)
        ],
        state.PHONE_NUMBER: [
            CommandHandler("start", start),
            MessageHandler(Filters.text, get_phone_number),
            MessageHandler(Filters.contact, get_phone_number)
        ],
        state.ADDRESS: [
            MessageHandler(Filters.location, get_address)
        ],
        state.CONFIRM_ADDRESS: [
            MessageHandler(Filters.text, confirm_address)
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
