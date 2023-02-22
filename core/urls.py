from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from .schema import swagger_urlpatterns

urlpatterns = [
    path("", admin.site.urls),
    path('bot/', include('apps.bot.urls')),
]

urlpatterns += swagger_urlpatterns

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += swagger_urlpatterns

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r'^rosetta/', include('rosetta.urls'))
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
