from django.conf import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from django.utils.translation import gettext_lazy as _

from apps.bot.models import Region, City
from core.settings.base import BOT_TOKEN as token
from telegram import Bot


def join_channel_links():
    channels = settings.TELEGRAM_CHANNELS
    bot = Bot(token=token)
    data = []
    for i in channels:
        # get channels link and name
        channel = bot.get_chat(i)
        data.append([InlineKeyboardButton(text=channel.title, url=channel.invite_link)])
        print(channel.title, channel.invite_link)
    data.append([InlineKeyboardButton(text=str(_("Tekshirish")), callback_data="check")])
    return InlineKeyboardMarkup(
        data
    )


def regions_keyboard():
    data = []
    regions = Region.objects.filter(is_active=True)
    res = []
    for i in regions:
        res.append(InlineKeyboardButton(text=i.title, callback_data=i.id))
        if len(res) == 2:
            data.append(res)
            res = []
    if res:
        data.append(res)
    return InlineKeyboardMarkup(
        data
    )


def tumans_keyboard(region: Region):
    data = []
    res = []
    for i in City.objects.filter(region=region, is_active=True):
        res.append(InlineKeyboardButton(text=i.title, callback_data=i.id))
        if len(res) == 2:
            data.append(res)
            res = []
    if res:
        data.append(res)
    return InlineKeyboardMarkup(
        data
    )


def products_keyboard(products: list):
    data = []
    res = []
    for i in products:
        res.append(InlineKeyboardButton(text=i.title, callback_data=i.id))
        if len(res) == 2:
            data.append(res)
            res = []
    if res:
        data.append(res)
    return InlineKeyboardMarkup(
        data
    )


def buy_product(product):
    data = []
    res = []
    res.append(InlineKeyboardButton(text=str(_("Buyurtma berish")), callback_data=product.id))
    data.append(res)
    return InlineKeyboardMarkup(
        data
    )
