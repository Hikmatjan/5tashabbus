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
    data.append(
        [
            InlineKeyboardButton(text=str(_("Orqaga")), callback_data="back"),
        ]
    )
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
    data.append(
        [
            InlineKeyboardButton(text=str(_("Orqaga")), callback_data="back"),
        ]
    )
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

    data.append(
        [
            InlineKeyboardButton(text=str(_("Orqaga")), callback_data="back"),
        ]
    )
    return InlineKeyboardMarkup(
        data
    )


def buy_product(product, quantity=1):
    data = []
    res = [InlineKeyboardButton(text=str(_("➖")), callback_data=f"minus"),
           InlineKeyboardButton(text=f"{quantity}", callback_data=f"quantity_{product.id}"),
           InlineKeyboardButton(text=str(_("➕")), callback_data=f"plus")]
    data.append(res)
    res = [InlineKeyboardButton(text=str(_("Savatchaga qo'shish")), callback_data='add_to_cart')]
    data.append(res)
    data.append(
        [
            InlineKeyboardButton(text=str(_("Orqaga")), callback_data="back"),
        ]
    )
    return InlineKeyboardMarkup(
        data
    )


def main_buttons():
    data = [
        [InlineKeyboardButton(text=str(_("Mahsulot sotib olish")), callback_data="buy_product")],
        [InlineKeyboardButton(text=str(_("Savatcha")), callback_data="savatcha"),
         InlineKeyboardButton(text=str(_("Mening buyurtmalarim")), callback_data="my_orders")],
        [InlineKeyboardButton(text=str(_("Biz haqimizda")), callback_data="about_us")],
    ]

    return InlineKeyboardMarkup(
        data
    )


def back_to_main():
    data = [
        [InlineKeyboardButton(text=str(_("Orqaga")), callback_data="back")],
    ]

    return InlineKeyboardMarkup(
        data
    )


def order_buttons(order):
    data = [
        [InlineKeyboardButton(text=str(_("Buyurtmani tasdiqlash")), callback_data=f"confirm_order")],
        [InlineKeyboardButton(text=str(_("Buyurtmani davom ettirish")), callback_data=f"continue_order")],
        [InlineKeyboardButton(text=str(_("Tozalash")), callback_data=f"clear_order")],
    ]
    items = order.items.all()
    if items:
        for i in items:
            res = [
                InlineKeyboardButton(text=str(_("➖")), callback_data=f"minus_{i.id}"),
                InlineKeyboardButton(text=f"{i.product.title}", callback_data=f"product"),
                InlineKeyboardButton(text=str(_("➕")), callback_data=f"plus_{i.id}"),
            ]
            data.append(res)
    data.append(
        [
            InlineKeyboardButton(text=str(_("Orqaga")), callback_data="back"),
        ]
    )
    return InlineKeyboardMarkup(
        data
    )
