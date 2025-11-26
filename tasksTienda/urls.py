
#urls tienda
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views_api
from . import views

app_name = 'tienda'

urlpatterns = [

    #Ingreso Tienda
    path('signupTienda/', views.signupTienda, name='signupTienda'),
    path('signinTienda/', views.signinTienda, name='signinTienda'),
    path('signoutTienda/', views.signoutTienda, name='signoutTienda'),
    path('productos/', views.productos_por_tienda, name='productos_tienda_list'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),


    # Tienda urls
    path('dashboard/', views.dashboard_tienda, name='dashboard_tienda'),

    # api keys
    path('api/obtener-api-key/', views_api.obtener_api_key, name='obtener_api_key'),
    path('api/recibir-producto/', views_api.recibir_producto, name='recibir_producto'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)