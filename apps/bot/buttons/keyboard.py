from telegram import ReplyKeyboardMarkup, KeyboardButton
from django.utils.translation import gettext_lazy as _


def request_phone_button():
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    text=str(_("📞Telefon raqamni yuborish")),
                    request_contact=True,
                    one_time_keyboard=True,
                )
            ]
        ],
        resize_keyboard=True,
    )


def back_button():
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(text=str(_("⬅️Orqaga")))
            ]
        ],
        resize_keyboard=True,
    )

