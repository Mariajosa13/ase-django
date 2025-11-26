from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('cliente:productos')),
    path('admin/', admin.site.urls),
    
    path('cliente/', include(('tasksCliente.urls', 'cliente'), namespace='cliente')),
    path('tienda/', include(('tasksTienda.urls', 'tienda'), namespace='tienda')),
    path('domiciliario/', include(('tasksDomiciliario.urls', 'domiciliario'), namespace='domiciliario')),
]