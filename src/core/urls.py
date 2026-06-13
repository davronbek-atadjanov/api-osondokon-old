from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.i18n import set_language
from apps.payments.views.payme import PaymeCallBackAPIView
from apps.payments.views.click import ClickWebhookAPIView
from apps.telegrambot.views import telegram_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path('payments/payme/update/', PaymeCallBackAPIView.as_view()),
    path('payments/click/update/', ClickWebhookAPIView.as_view()),
    path('telegram-webhook/<int:bot_id>/', telegram_webhook),
    path('set_language/', set_language, name='set_language'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)