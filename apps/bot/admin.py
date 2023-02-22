from django.contrib import admin
from .models import Region, City, TelegramUser, Product, Order, OrderItem


# Register your models here.

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active']
    list_display_links = ['id', 'title']
    list_editable = ['is_active']
    search_fields = ['title']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'region', 'is_active']
    list_display_links = ['id', 'title']
    list_editable = ['is_active']
    list_filter = ['region']
    autocomplete_fields = ['region']
    search_fields = ['title']


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_active']
    list_display_links = ['id', 'telegram_id']
    list_filter = ['is_active']
    search_fields = ['username', 'first_name', 'last_name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'city', 'title', 'price', 'is_active']
    list_display_links = ['id', 'title']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    autocomplete_fields = ['city']
