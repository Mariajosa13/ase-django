from django.contrib import admin
from django.urls import path
from tasksCliente import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),

    # Ingreso cliente
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),

    # Perfil cliente
    path('perfil/', views.perfil_detalle, name='perfil_detalle'),
    path('perfil/editar/', views.perfil_editar, name='perfil_editar'),
    path('perfil/eliminar/<str:campo>/', views.eliminar_campo, name='eliminar_campo'),

    # Productos
    path('productos/', views.productos, name='productos'),
    path('mascotas/producto_list', views.producto_list, name='producto_list'),
    path('productos/categoriaMascota/<slug:slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('productos/<int:producto_id>/', views.producto_detail, name='producto_detail'),
    path('productos/<slug:slug>/', views.producto_detail, name='detalle_producto_mascota'),

    # Vista domi después de ingreso
    path('domi/', views.dashboard_domiciliario, name='dashboard_domiciliario')

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)