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


    def __str__(self):
        return self.telegram_id

    class Meta:
        verbose_name = _("Telegram User")
        verbose_name_plural = _("Telegram Users")

