import logging

from django.conf import settings
from django.utils import timezone
from telegram import Update, ReplyKeyboardRemove, Bot
from telegram.ext import CallbackContext

from apps.bot.buttons.inlines import join_channel_links, regions_keyboard
from apps.bot.models import TelegramUser
from apps.bot.states import state
from utils.decarators import get_member
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def check_member_joins(bot: Bot, tg_user: TelegramUser):
    channels = settings.TELEGRAM_CHANNELS
    admins = settings.TELEGRAM_ADMINS
    for i in channels:
        try:
            # check if user is member of channel
            print(bot.get_chat_member(chat_id=i, user_id=tg_user.telegram_id).status)
            if bot.get_chat_member(chat_id=i, user_id=tg_user.telegram_id).status not in ["member", 'creator',
                                                                                          'administrator']:
                return False
        # chat not found
        except Exception as e:
            logger.error(e)
            for j in admins:
                bot.send_message(chat_id=j, text=str(_("Kanal topilmadi")) + f" {bot.get_chat(i).title}")
            continue
    return True

    # check if user is member of channel


@get_member
def start(update: Update, context: CallbackContext, tg_user: TelegramUser):
    """Send a message when the command /start is issued."""
    update.message.reply_html(
        text=str(
            _("Assalomu alaykum 5 tashabbus botiga xush kelibsiz."))
    )
    if not check_member_joins(bot=context.bot, tg_user=tg_user):
        update.message.reply_html(
            text=str(
                _("Bot ishlatish uchun kanallarga a'zo bo'lishingiz kerak.")), reply_markup=join_channel_links()
        )
        return state.JOIN_CHANNELS
    update.message.reply_html(
        text=str(
            _("Quyidagi viloyatlardan birini tanlang.")),
        reply_markup=regions_keyboard()
    )
    return state.CHOOSE_REGION


@get_member
def check_join_channel(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    if check_member_joins(bot=context.bot, tg_user=tg_user):
        query.edit_message_text(
            text=str(_("Quyidagi viloyatlardan birini tanlang")), reply_markup=regions_keyboard()
        )
        return state.CHOOSE_REGION
    else:
        update.callback_query.answer("Hamma kanallarga a'zo bo'ling va qaytadan tekshirish tugmasini bosing")
        return state.JOIN_CHANNELS
