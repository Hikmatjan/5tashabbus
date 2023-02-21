from django.utils.translation import activate

from apps.bot import models


def get_member(func):
    def wrap(update, context, *args, **kwargs):
        try:
            user_id = update.message.chat_id
        except AttributeError:
            user_id = update.callback_query.message.chat_id
        user, created = models.TelegramUser.objects.get_or_create(
            telegram_id=user_id,
            defaults={
                'first_name': update.effective_user.first_name,
                'last_name': update.effective_user.last_name,
                'username': update.effective_user.username,
            }
        )
        if not created:
            user.first_name = update.effective_user.first_name
            user.last_name = update.effective_user.last_name
            user.username = update.effective_user.username
            user.save()
        activate('uz')
        return func(update, context, user, *args, **kwargs)

    return wrap
