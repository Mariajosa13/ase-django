from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'domiciliario'


urlpatterns = [

    # Domi urls
    path('completar_perfil/', views.completar_perfil, name='completar_perfil'),
    path('dashboard/', views.domiciliario_dashboard, name='dashboard'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)