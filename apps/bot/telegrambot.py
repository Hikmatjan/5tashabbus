import logging

import requests
from PIL import Image
from django.conf import settings
from django.utils import timezone
from telegram import Update, ReplyKeyboardRemove, Bot
from telegram.ext import CallbackContext

from apps.bot.buttons.inlines import join_channel_links, regions_keyboard, tumans_keyboard, products_keyboard, \
    buy_product, main_buttons, back_to_main, order_buttons
from apps.bot.buttons.keyboard import request_phone_button, request_location_button, confirm_address_button
from apps.bot.models import TelegramUser, Region, Product, City, Order, OrderItem, OrderStatus
from apps.bot.states import state
from utils.decarators import get_member
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def check_member_joins(bot: Bot, tg_user: TelegramUser):
    channels = settings.TELEGRAM_CHANNELS
    admins = settings.TELEGRAM_ADMINS
    for i in channels:
        try:
            if bot.get_chat_member(chat_id=i, user_id=tg_user.telegram_id).status not in ["member", 'creator',
                                                                                          'administrator']:
                return False
        except Exception as e:
            logger.error(e)
            try:
                for j in admins:
                    bot.send_message(chat_id=j, text=str(_("Kanal topilmadi")) + f" {i}")
            except Exception as e:
                print(e)
                pass
            continue
    return True

    # check if user is member of channel


@get_member
def start(update: Update, context: CallbackContext, tg_user: TelegramUser):
    """Send a message when the command /start is issued."""
    if not check_member_joins(bot=context.bot, tg_user=tg_user):
        update.message.reply_html(
            text=str(
                _("Assalomu alaykum 5 tashabbus botiga xush kelibsiz.Bot ishlatish uchun "
                  "kanallarga a'zo bo'lishingiz kerak.")),
            reply_markup=join_channel_links()
        )
        return state.JOIN_CHANNELS
    # update.message.reply_html(
    #     text=str(
    #         _("Quyidagi viloyatlardan birini tanlang.")),
    #     reply_markup=regions_keyboard()
    # )
    update.message.reply_html(
        text=str(
            _("Assalomu alaykum 5 tashabbus botiga xush kelibsiz. Ushbu bot orqali siz mahsulotlarni sotib "
              "olishingiz mumkin")),
        reply_markup=main_buttons()
    )
    return state.MAIN_MENU


@get_member
def main_menu(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    data = query.data
    if data == "buy_product":
        query.edit_message_text(
            text=str(_("Quyidagi viloyatlardan birini tanlang.")),
            reply_markup=regions_keyboard())
        return state.CHOOSE_REGION
    elif data == "my_orders":
        query.edit_message_text(
            text=str(_("Sizning buyurtmalar")),
            reply_markup=main_buttons()
        )
        return state.MAIN_MENU
    elif data == "savatcha":
        order = Order.objects.filter(user=tg_user, status=OrderStatus.NEW).first()
        if order and order.items.count() > 0:
            text = str(_("Sizning savatchangizda quyidagi mahsulotlar bor:\n\n"))
            total = 0
            for i in order.items.all():
                text += f"{i.product.title} x {i.quantity}  = {int(i.quantity * i.product.price)} so'm\n"
                total += int(i.quantity * i.product.price)
            text += f"{str(_('Umumiy summa'))}: {total} so'm"
            query.edit_message_text(
                text=text,
                reply_markup=order_buttons(order)
            )
            return state.SAVATCHA
        else:
            query.edit_message_text(
                text=str(_("Sizning savatchangiz bo'sh")),
                reply_markup=main_buttons()
            )
            return state.MAIN_MENU
    else:
        query.edit_message_text(
            text=str(_("Biz haqimizda malumot!!!")),
            reply_markup=back_to_main()
        )
        return state.ABOUT_US


@get_member
def savatcha(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    data = query.data
    if data == 'back':
        query.edit_message_text(
            text=str(_("Asosiy Menu")),
            reply_markup=main_buttons()
        )
        return state.MAIN_MENU
    elif data == 'clear_order':
        order = Order.objects.filter(user=tg_user, status=OrderStatus.NEW).first()
        if order:
            order.delete()
        query.edit_message_text(
            text=str(_("Savatcha tozalandi")),
            reply_markup=main_buttons()
        )
        return state.MAIN_MENU
    elif data == 'continue_order':
        query.edit_message_text(
            text=str(_("Buyurtma berishni davom ettirishingiz mumkin")),
            reply_markup=main_buttons()
        )
        return state.MAIN_MENU
    elif data == 'confirm_order':
        query.message.delete()
        query.message.reply_html(
            text=str(_("Siz bilan bog'lasnish uchun telefon raqamingizni yuboring")),
            reply_markup=request_phone_button()
        )
        return state.PHONE_NUMBER
    elif data == 'product':
        return state.SAVATCHA
    else:
        text, item = data.split("_")
        item = OrderItem.objects.filter(id=int(item)).first()
        if text == 'plus':
            quantity = item.quantity + 1
            if quantity > item.product.quantity:
                query.answer(text=str(_("Mahsulot yetarli emas")))
                return state.SAVATCHA
            item.quantity = quantity
        else:
            quantity = item.quantity - 1
            if quantity <= 0:
                query.answer(text=str(_("Mahsulot soni 0 dan kichik bo'lishi mumkin emas")))
                return state.SAVATCHA
            item.quantity = quantity
        item.save()
        order = Order.objects.filter(user=tg_user, status=OrderStatus.NEW).first()
        text = str(_("Sizning savatchangizda quyidagi mahsulotlar bor:\n\n"))
        total = 0
        for i in order.items.all():
            text += f"{i.product.title} x {i.quantity}  = {int(i.quantity * i.product.price)} so'm\n"
            total += int(i.quantity * i.product.price)
        text += f"{str(_('Umumiy summa'))}: {total} so'm"
        query.edit_message_text(
            text=text,
            reply_markup=order_buttons(order)
        )
        return state.SAVATCHA


def validate_phone(phone_number: str):
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    if phone_number.startswith("998"):
        phone_number = phone_number[3:]
    if phone_number.startswith("8"):
        phone_number = phone_number[1:]
    if phone_number.startswith("9"):
        phone_number = phone_number[1:]
    if phone_number.startswith("0"):
        phone_number = phone_number[1:]
    if len(phone_number) == 9:
        return True
    return False


@get_member
def get_phone_number(update: Update, context: CallbackContext, tg_user: TelegramUser):
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
        if not validate_phone(phone_number):
            update.message.reply_text(
                text=str(_("Raqamni to'g'ri kiriting"))
            )
            return state.PHONE_NUMBER
    order = Order.objects.filter(user=tg_user, status=OrderStatus.NEW).first()
    if order:
        order.phone = phone_number
        order.save()
        update.message.reply_html(
            text=str(_("Buyurtmani yakunlash uchun manzilingizni yuboring")),
            reply_markup=request_location_button()
        )
        return state.ADDRESS
    else:
        update.message.reply_html(
            text=str(_("Sizning savatchangiz bo'sh")),
            reply_markup=main_buttons()
        )
        return state.MAIN_MENU


def get_address_by_long_lat(longitude: float, latitude: float):
    url = f"https://uzmap.xn--h28h.uz/reverse?format=jsonv2&lat={latitude}&lon={longitude}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("display_name")
    return None


@get_member
def get_address(update: Update, context: CallbackContext, tg_user: TelegramUser):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    address = get_address_by_long_lat(longitude, latitude)
    update.message.reply_html(
        text=str(_("Manzilingiz: ")) + address + str(_("\nBuyurtmani yakunlash uchun tasdiqlang")),
        reply_markup=confirm_address_button()
    )
    context.user_data['address'] = address
    context.user_data['latitude'] = latitude
    context.user_data['longitude'] = longitude
    return state.CONFIRM_ADDRESS


@get_member
def confirm_address(update: Update, context: CallbackContext, tg_user: TelegramUser):
    message = update.message.text
    print(message)
    if message == str(_("✅Tasdiqlash")):
        order = Order.objects.filter(user=tg_user, status=OrderStatus.NEW).first()
        if order:
            order.address = context.user_data['address']
            order.latitude = context.user_data['latitude']
            order.longitude = context.user_data['longitude']
            order.status = OrderStatus.ACCEPTED
            order.save()
            message = f"Yangi buyurtma\n\n" \
                      f"Buyurtmachi: {order.user.full_name}\n" \
                      f"Telefon: {order.phone}\n" \
                      f"Manzil: {order.address}\n" \
                      f"Mahsulotlar:\n"
            total = 0
            for item in order.items.all():
                message += f"{item.product.title} x {item.quantity} = {int(item.quantity * item.product.price)} so'm\n"
                total += int(item.quantity * item.product.price)
            message += f"{str(_('Umumiy summa'))}: {int(total)} so'm"
            group_id = settings.GROUP_ID
            context.bot.send_message(
                chat_id=group_id,
                text=message
            )
            context.bot.send_location(
                chat_id=group_id,
                latitude=order.latitude,
                longitude=order.longitude
            )
            update.message.reply_html(
                text=str(_("Buyurtma qabul qilindi")),
                reply_markup=main_buttons()
            )
            return state.MAIN_MENU
        else:
            update.message.reply_html(
                text=str(_("Sizning savatchangiz bo'sh")),
                reply_markup=main_buttons()
            )
            return state.MAIN_MENU
    else:
        update.message.reply_html(
            text=str(_("Manzilingizni qayta yuboring")),
            reply_markup=request_location_button()
        )
        return state.ADDRESS


@get_member
def about_us_button(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    query.edit_message_text(
        text=str(_("Assalomu alaykum 5 tashabbus botiga xush kelibsiz. Ushbu bot orqali siz mahsulotlarni sotib "
                   "olishingiz mumkin")),
        reply_markup=main_buttons()
    )
    return state.MAIN_MENU


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


@get_member
def get_region(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    data = query.data
    if data == 'back':
        query.edit_message_text(
            text=str(_("Mahsulot sotib olish uchun Buyurtma berish tugmasini bosing")),
            reply_markup=main_buttons()
        )
        return state.MAIN_MENU
    try:
        if data.isdigit() and data != "0":
            region = Region.objects.get(id=int(data))
            query.edit_message_text(
                text=str(_("Quyidagi tumanlardan birini tanlang ")),
                reply_markup=tumans_keyboard(region)
            )
            return state.CHOOSE_TUMAN
    except Exception as e:
        logger.error(e)
        query.edit_message_text(
            text=str(_("Quyidagi viloyatlardan birini tanlang")), reply_markup=regions_keyboard()
        )
        return state.CHOOSE_REGION


@get_member
def get_tuman(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    data = query.data
    if data == 'back':
        query.edit_message_text(
            text=str(_("Quyidagi viloyatlardan birini tanlang")), reply_markup=regions_keyboard()
        )
        return state.CHOOSE_REGION
    if data.isdigit():
        tuman = City.objects.get(id=int(data))
        context.user_data['region'] = tuman.region_id
        context.user_data['tuman'] = tuman.id
        products = Product.objects.filter(city=tuman, is_active=True)
        if products:
            query.edit_message_text(
                text=str(_("Ushbu tumandagi quyidagi mahsulotlardan birini tanlang")),
                reply_markup=products_keyboard(products)
            )
            return state.CHOOSE_PRODUCT
        else:
            query.answer(str(_("Mahsulotlar topilmadi Iltimos boshqa tumani tanlang")))
            return state.CHOOSE_TUMAN


@get_member
def get_product(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    data = query.data
    if data == 'back':
        region = Region.objects.get(id=context.user_data['region'])
        query.edit_message_text(
            text=str(_("Quyidagi tumanlardan birini tanlang ")),
            reply_markup=tumans_keyboard(region)
        )
        return state.CHOOSE_TUMAN
    if data.isdigit():
        quantity = 1
        context.user_data['quantity'] = quantity
        product = Product.objects.get(id=int(data))
        context.user_data['product'] = product.id
        message = str(_("Mahsulot haqida qisqacha malumot\n<b>Mahsulot nomi:</b>")) + product.title + str(
            _("\n<b>Mahsulot narxi:</b> ")) + str(product.price) + str(
            _("\n<b>Mahsulot haqida qisqacha:</b> ")) + product.description + str(
            _("\n<b>Mahsulot soni:</b> ")) + str(
            product.quantity) + f"\n\n{int(product.price)} x {quantity} = {int(product.price * quantity)}\n\n" + str(
            _("Jamis summa: ")) + str(
            product.price * quantity)
        image = product.image
        query.message.delete()
        if image:
            context.bot.send_photo(chat_id=tg_user.telegram_id, photo=open(image.path, 'rb'), caption=message,
                                   parse_mode="HTML", reply_markup=buy_product(product))
        else:
            context.bot.send_message(chat_id=tg_user.telegram_id, text=message, parse_mode="HTML",
                                     reply_markup=buy_product(product))
        return state.BUY_PRODUCT


@get_member
def add_product_to_savatcha(update: Update, context: CallbackContext, tg_user: TelegramUser):
    query = update.callback_query
    data = query.data
    product = Product.objects.get(id=context.user_data['product'])
    if data == 'back':
        tuman = City.objects.get(id=context.user_data['tuman'])
        products = Product.objects.filter(city=tuman, is_active=True)
        if products:
            if product.image:
                query.message.delete()
                query.message.reply_html(
                    text=str(_("Ushbu tumandagi quyidagi mahsulotlardan birini tanlang")),
                    reply_markup=products_keyboard(products)
                )
            else:
                query.edit_message_text(
                    text=str(_("Ushbu tumandagi quyidagi mahsulotlardan birini tanlang")),
                    reply_markup=products_keyboard(products)
                )
            return state.CHOOSE_PRODUCT
        else:
            query.answer(str(_("Mahsulotlar topilmadi Iltimos boshqa tumani tanlang")))
            return state.CHOOSE_TUMAN
    if data == 'add_to_cart':
        quantity = context.user_data['quantity']
        if product.quantity < quantity:
            query.answer(str(_("Mahsulotlar soni yetarli emas")))
            return state.BUY_PRODUCT
        else:
            cart, created = Order.objects.get_or_create(user=tg_user, status=OrderStatus.NEW)
            cart_item, created = OrderItem.objects.get_or_create(order=cart, product=product)
            cart_item.quantity += quantity
            cart_item.price = product.price
            cart_item.save()
            if product.image:
                query.message.delete()
                query.message.reply_html(
                    text=str(_("Mahsulot savatchaga qo'shildi")),
                    reply_markup=main_buttons()
                )
            else:
                query.edit_message_text(
                    text=str(_("Mahsulot savatchaga qo'shildi")),
                    reply_markup=main_buttons(),
                    parse_mode="HTML"
                )
            return state.MAIN_MENU
    elif data == 'plus':
        quantity = context.user_data['quantity']
        quantity += 1
        if quantity > product.quantity:
            query.answer(str(_("Mahsulotlar soni yetarli emas")))
            return state.BUY_PRODUCT
        context.user_data['quantity'] = quantity
    elif data == 'minus':
        quantity = context.user_data['quantity']
        quantity -= 1
        if quantity < 1:
            query.answer(str(_("Mahsulotlar soni yetarli emas")))
            return state.BUY_PRODUCT
        context.user_data['quantity'] = quantity
    else:
        return state.BUY_PRODUCT
    product = Product.objects.get(id=context.user_data['product'])
    message = str(_("Mahsulot haqida qisqacha malumot\n<b>Mahsulot nomi:</b>")) + product.title + str(
        _("\n<b>Mahsulot narxi:</b> ")) + str(product.price) + str(
        _("\n<b>Mahsulot haqida qisqacha:</b> ")) + product.description + str(
        _("\n<b>Mahsulot soni:</b> ")) + str(
        product.quantity) + f"\n\n{int(product.price)} x {quantity} = {int(product.price * quantity)}\n\n" + str(
        _("Jamis summa: ")) + str(
        int(product.price * quantity))
    image = product.image
    if image:
        query.edit_message_caption(
            caption=message,
            parse_mode="HTML",
            reply_markup=buy_product(product, quantity)
        )
    else:
        query.edit_message_text(
            text=message,
            parse_mode="HTML",
            reply_markup=buy_product(product, quantity)
        )
    return state.BUY_PRODUCT
