from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from tasks import views_api 

app_name = 'domiciliario'


urlpatterns = [

    # Domi urls
    path('completar_perfil/', views.completar_perfil, name='completar_perfil'),
    path('dashboard/', views.domiciliario_dashboard, name='dashboard'),

    # path('auth/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # La vista para el JWT
    
    # pedidos cercanos
    path('pedidos/cercanos/', views_api.pedidos_cercanos_domiciliario, name='pedidos_cercanos'),
    
    # acción pedido
    path('pedidos/tomar/<int:pedido_id>/', views_api.tomar_pedido, name='tomar_pedido'),
    path('pedidos/confirmar-recogida/<int:pedido_id>/', views_api.confirmar_recogida, name='confirmar_recogida'),
    path('pedidos/confirmar-entrega/<int:pedido_id>/', views_api.confirmar_entrega, name='confirmar_entrega'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)