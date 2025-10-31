from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tasks import views_api

urlpatterns = [
    path('api/recibir-producto/', views_api.recibir_producto, name='recibir_producto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)