from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from apps.bot.views import HandleWebhook

urlpatterns = [
    path('webhook/', csrf_exempt(HandleWebhook.as_view()), name='telegram_webhook'),
]
