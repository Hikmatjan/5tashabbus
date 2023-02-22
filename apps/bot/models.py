from django.conf import settings
from django.db import models
from apps.common.models import BaseModel
from django.utils.translation import gettext_lazy as _


class Region(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


class City(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities', verbose_name=_("Region"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")


class TelegramUser(BaseModel):
    telegram_id = models.CharField(max_length=255, verbose_name=_("Telegram ID"))
    first_name = models.CharField(max_length=255, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=255, verbose_name=_("Last Name"), null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Username"))
    phone_number = models.CharField(max_length=255, verbose_name=_("Phone Number"), null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    def __str__(self):
        return self.telegram_id

    class Meta:
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")


class Product(BaseModel):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='products', verbose_name=_("City"))
    price = models.FloatField(verbose_name=_("Price"))
    quantity = models.IntegerField(verbose_name=_("Quantity"))
    image = models.ImageField(upload_to='products/', verbose_name=_("Image"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return self.title
    @property
    def get_image_url(self):
        HOST = settings.WEBHOOK_URL
        return f"{HOST}{self.image.url}"

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class OrderStatus(models.TextChoices):
    NEW = 'NEW', _('New')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    CANCELED = 'CANCELED', _('Canceled')
    DELIVERED = 'DELIVERED', _('Delivered')


class Order(BaseModel):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='orders', verbose_name=_("User"))
    status = models.CharField(max_length=255, verbose_name=_("Status"), choices=OrderStatus.choices,
                              default=OrderStatus.NEW)
    phone = models.CharField(max_length=255, verbose_name=_("Phone"), null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name=_("Address"), null=True, blank=True)
    longitute = models.FloatField(verbose_name=_("Longitute"), null=True, blank=True)
    latitude = models.FloatField(verbose_name=_("Latitude"), null=True, blank=True)

    def __str__(self):
        return self.user.first_name

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("Order"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders', verbose_name=_("Product"))
    quantity = models.IntegerField(verbose_name=_("Quantity"), default=0)
    price = models.FloatField(verbose_name=_("Buyed Price"), default=0)

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
