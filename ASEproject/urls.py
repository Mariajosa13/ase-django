"""
URL configuration for ASEproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('productos/', views.productos, name='productos'),
    path('mascotas/producto_list', views.producto_list, name='producto_list'),
    path('mascotas/producto/<slug:slug>/resena/', views.agregar_resena, name='agregar_resena'),
    path('productos/categoriaMascota/<slug:slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('productos/<int:producto_id>/', views.producto_detail, name='producto_detail'),
    path('productos/<slug:slug>/', views.producto_detail, name='detalle_producto_mascota'),
    path('productos/<int:producto_id>/delete', views.delete_producto, name='delete_producto'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)