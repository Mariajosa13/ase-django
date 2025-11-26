from django.urls import path
from tasksCliente import views
from django.conf import settings
from django.conf.urls.static import static

# #importacion vistas API
# from tasks.views_api import (
#     SignupAPIView, ProfileDetailAPIView, ProfileUpdateAPIView,
#     DeleteProfileFieldAPIView, ProductosViewSet, CategoriaMascotaViewSet,
#     ResenaProductoMascotaViewSet, MyTokenObtainPairAPIView
# )

# Crea un router para ViewSets
# router = DefaultRouter()
# router.register(r'productos', ProductosViewSet)
# router.register(r'categorias', CategoriaMascotaViewSet)
# router.register(r'resenas', ResenaProductoMascotaViewSet)

app_name = 'cliente'


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

    #CRUD Direccion
    path('direccion/', views.lista_direcciones, name='lista_direcciones'),
    path('direccion/agregar/', views.agregar_direccion, name='agregar_direccion'),
    path('direccion/<int:direccion_id>/', views.direccion_detalle, name='direccion_detalle'),
    path('direccion/<int:direccion_id>/editar/', views.direccion_editar, name='direccion_editar'),
    path('direccion/<int:direccion_id>/eliminar/', views.direccion_eliminar, name='direccion_eliminar'),
    
    # Productos
    path('productos/', views.productos, name='productos'),
    path('mascotas/producto_list', views.producto_list, name='producto_list'),
    path('productos/categoriaMascota/<slug:slug>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('productos/<int:producto_id>/', views.producto_detail, name='producto_detail'),
    path('productos/<slug:slug>/', views.producto_detail, name='detalle_producto_mascota'),

     # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:producto_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('checkout/', views.checkout, name='checkout'),

    # # URLs de la API 
    # path('api/', include(router.urls)),

    # # URLs de autenticación JWT
    # path('api/token/', MyTokenObtainPairAPIView.as_view(), name='api_token_obtain_pair'), #signin
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'), 

    # # URLs específicas de gestión de usuarios/perfiles API
    # path('api/register/', SignupAPIView.as_view(), name='api_register'), #signup
    # path('api/profile/', ProfileDetailAPIView.as_view(), name='api_profile_detail'), #profile
    # path('api/profile/update/', ProfileUpdateAPIView.as_view(), name='api_profile_update'), #profile_update
    # path('api/profile/delete-field/<str:campo>/', DeleteProfileFieldAPIView.as_view(), name='api_delete_profile_field'), #profile_delete_field
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    
    