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


def request_location_button():
    return ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(
                    text=str(_("📍Manzilni yuborish")),
                    request_location=True,
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

def confirm_address_button():
    return ReplyKeyboardMarkup(
        [
            [
                str(_("✅Tasdiqlash")),
                str(_("❌Qayta yuborish")),
            ]
        ],
        resize_keyboard=True,
    )
