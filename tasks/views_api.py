import secrets
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Avg
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction

#Geolocalización

from rest_framework.decorators import api_view
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.response import Response
from rest_framework import status

# Importa los modelos generales de 'tasks'
from .models import Profile, CategoriaMascota, Productos, ResenaProductoMascota, Cliente, Domiciliario, Tienda, Pedido, ApiKey

from .serializers_api import (
    # SignupAPISerializer, ProfileSerializer, ClienteSpecificSerializer,
    # DomiciliarioSpecificSerializer, TiendaSpecificSerializer,
    # CategoriaMascotaSerializer, ProductosSerializer, ResenaProductoMascotaSerializer,
    # MyTokenObtainPairSerializer
    PedidoGeoSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

@api_view(['POST'])
def recibir_producto(request):
    api_key = request.headers.get('Authorization')

    if not api_key:
        return Response({'error': 'No API Key provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        api_key_obj = ApiKey.objects.get(key=api_key)
    except ApiKey.DoesNotExist:
        return Response({'error': 'Invalid API Key'}, status=status.HTTP_401_UNAUTHORIZED)
    
    tienda = api_key_obj

    nombre_producto = request.data.get('nombre')
    descripcion_producto = request.data.get('descripcion')
    precio_producto = request.data.get('precio')
    stock_producto = request.data.get('stock')
    imagen_producto = request.data.get('imagen')
    categoria_producto = request.data.get('categoria')
    tipo_mascota_producto = request.data.get('tipo_mascota')
    destacado_producto = request.data.get('destacado')
    fechaVencimiento_producto = request.data.get('fechaVencimiento')
    important_producto = request.data.get('important')
    datos_extra_producto = request.data.get('datos_extra', {})

    campos = {
        'nombre': nombre_producto,
        'descripcion': descripcion_producto,
        'precio': precio_producto,
        'stock': stock_producto,
        'imagen': imagen_producto,
        'categoria': categoria_producto,
        'tipo_mascota': tipo_mascota_producto,
        'destacado': destacado_producto,
        'fechaVencimiento': fechaVencimiento_producto,
        'important': important_producto,
        'datos_extra': datos_extra_producto,
    }

    if not campos:
        return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

    producto = Productos.objects.create(
        tienda=api_key_obj.tienda,
        nombre=nombre_producto,
        descripcion=descripcion_producto,
        precio=precio_producto,
        stock=stock_producto,
        imagen=imagen_producto,
        categoria=categoria_producto,
        tipo_mascota=tipo_mascota_producto,
        destacado=destacado_producto,
        fechaVencimiento=fechaVencimiento_producto,
        important=important_producto,
        datos_extra=datos_extra_producto
    )

    return Response({'message': 'Producto creado exitosamente', 'producto_id': producto.id}, status=status.HTTP_201_CREATED)



def generar_codigo():
    # Asegura un código de 6 dígitos con ceros iniciales
    return f"{secrets.randbelow(1000000):06d}"

    # pedido.codigo_entrega_tienda = generar_codigo()
    # pedido.codigo_recepcion_cliente = generar_codigo()
    # pedido.save()

@api_view(['POST'])
def pedidos_cercanos_domiciliario(request):
    # obtener coordenadas del domiciliario desde petición POST
    try:
        lat = float(request.data.get('latitude'))
        lng = float(request.data.get('longitude'))
    # se crea objeto Ponit de PostGis con las coordenadas del domiciliario
        domiciliario_point = Point(lng, lat, srid=4326)
    except(TypeError, ValueError):
        return Response({"detail": "Coordenadas (latitude, longitude) requueridas y válidas"}, status=status.HTTP_400_BAD_REQUEST)

    #consultar pedidos disponibles y cercanos
    pedidos_disponibles = Pedido.objects.filter(
        estado='DISPONIBLE',
        #distancia máxima 5000m
        ubicacion_recodiga__distance_lte=(domiciliario_point, D(km=5))
    ).annotate(
        distance=Distance('ubicacion_recogida', domiciliario_point)
    ).order_by('distance')[:10] #mostrar los 10 más cercanos

    # pasar el punto para el cálculo de distancia en el serializer

    serializer = PedidoGeoSerializer(
        pedidos_disponibles,
        many=True,
        context={'domiciliario_point': domiciliario_point}
    )

    return Response(serializer.data)

@api_view(['POST'])
def tomar_pedido(request, pedido_id):
    domiciliario_profile = request.user.profile.domiciliario

    with transaction.atomic():
        pedido = get_object_or_404(Pedido, id=pedido_id)

        if pedido.estado == 'DISPONIBLE' and pedido.domiciliario_asignado is None:
            # asignar y cambiar estado
            pedido.domiciliario_asignado = domiciliario_profile
            pedido.estado = 'EN_CURSO'
            pedido.save()
            return Response({"detail": "Pedido asignado. Dirígete a la tienda.", "pedido_id": pedido.id}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "El pedido ya no está disponible."}, status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def confirmar_recogida(request, pedido_id):
    codigo_ingresado = request.data.get('codigo')

    with transaction.atomic():
        pedido = get_object_or_404(Pedido, id=pedido_id, domiciliario_asignado=request.user.profile.domiciliario)

        if pedido.estado == 'EN_CURSO' and codigo_ingresado == pedido.codigo_entrega_tienda:
            pedido.estado = 'EN_CAMINO'
            pedido.save()
            return Response({"detail": "Recogida confirmada. Inicia la ruta de entrega"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Código o estado de pedido incorrecto."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def confirmar_entrega(request, pedido_id):
    codigo_ingresado = request.data.get('codigo')

    with transaction.atomic():
        pedido = get_object_or_404(Pedido, id=pedido_id, domiciliario_asignado=request.user.profile.domiciliario)

        if pedido.estado == 'EN_CAMINO' and codigo_ingresado == pedido.codigo_recepcion_cliente:
            pedido.estado = 'ENTREGADO'
            # Nota: acá se puede registrar ganancias o comisiones
            pedido.save()
            return Response({"detail": "Entrega completada exitosamente. ¡Gracias!"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Codigo o estado de pedido incorrecto."}, status=status.HTTP_400_BAD_REQUEST)
#Vistas de Autenticación y Gestión de Usuarios API 

# class MyTokenObtainPairAPIView(TokenObtainPairView):
#     serializer_class = MyTokenObtainPairSerializer

# class SignupAPIView(generics.CreateAPIView):
#     serializer_class = SignupAPISerializer
#     permission_classes = [permissions.AllowAny]

# #vista de API para obtener el perfil del usuario autenticado
# class ProfileDetailAPIView(generics.RetrieveAPIView):

#     serializer_class = ProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         return self.request.user.profile
    
#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         profile_data = self.get_serializer(instance).data # Datos del Profile general

#         # Añadir datos del perfil específico
#         if instance.tipo_usuario == 'cliente':
#             cliente_profile = Cliente.objects.filter(profile=instance).first()
#             if cliente_profile:
#                 profile_data['rol_specific_data'] = ClienteSpecificSerializer(cliente_profile).data
#         elif instance.tipo_usuario == 'domiciliario':
#             domiciliario_profile = Domiciliario.objects.filter(profile=instance).first()
#             if domiciliario_profile:
#                 profile_data['rol_specific_data'] = DomiciliarioSpecificSerializer(domiciliario_profile).data
#         elif instance.tipo_usuario == 'tienda':
#             tienda_profile = Tienda.objects.filter(profile=instance).first()
#             if tienda_profile:
#                 profile_data['rol_specific_data'] = TiendaSpecificSerializer(tienda_profile).data
        
#         return Response(profile_data)

# # Vistas de API para actualizar el perfil del usuario autenticado
# class ProfileUpdateAPIView(generics.UpdateAPIView):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         return self.request.user.profile

#     def update(self, request, *args, **kwargs):
#         profile = self.get_object()
        
#         # Validar y actualizar los campos del Profile general
#         serializer = self.get_serializer(profile, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer) # Guarda los cambios del Profile

#         # Lógica para actualizar campos del perfil específico (Cliente, Domiciliario, Tienda)
#         if profile.tipo_usuario == 'cliente':
#             cliente, created = Cliente.objects.get_or_create(profile=profile)
#             cliente_serializer = ClienteSpecificSerializer(cliente, data=request.data, partial=True)
#             if cliente_serializer.is_valid():
#                 cliente_serializer.save()
#             else:
#                 print("Errores en datos de cliente:", cliente_serializer.errors)

#         elif profile.tipo_usuario == 'domiciliario':
#             domiciliario, created = Domiciliario.objects.get_or_create(profile=profile)
#             domiciliario_serializer = DomiciliarioSpecificSerializer(domiciliario, data=request.data, partial=True)
#             if domiciliario_serializer.is_valid():
#                 domiciliario_serializer.save()
#             else:
#                 print("Errores en datos de domiciliario:", domiciliario_serializer.errors)
        
#         elif profile.tipo_usuario == 'tienda':
#             tienda, created = Tienda.objects.get_or_create(profile=profile)
#             tienda_serializer = TiendaSpecificSerializer(tienda, data=request.data, partial=True)
#             if tienda_serializer.is_valid():
#                 tienda_serializer.save()
#             else:
#                 print("Errores en datos de tienda:", tienda_serializer.errors)

#         # Devolver una respuesta completa del perfil actualizado
#         return self.retrieve(request, *args, **kwargs) # Retrieve obtiene los detalles de un perfil en especifico

# # Vista de API para eliminar campos específicos del perfil del usuario autenticado
# class DeleteProfileFieldAPIView(generics.UpdateAPIView):
#     queryset = Profile.objects.all()
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         return self.request.user.profile

#     def patch(self, request, *args, **kwargs):
#         profile = self.get_object()
#         campo_a_eliminar = self.kwargs.get('campo')

#         campos_permitidos_cliente = ['segundo_apellido', 'celular', 'genero', 'fecha_nacimiento']
#         campos_permitidos_domiciliario = ['segundo_apellido', 'celular', 'genero', 'fecha_nacimiento', 'vehiculo']
#         related_profile_obj = None

#         if profile.tipo_usuario == 'cliente':
#             if campo_a_eliminar not in campos_permitidos_cliente:
#                 return Response({"detail": "No se puede eliminar este campo o no pertenece a tu tipo de usuario."}, status=status.HTTP_403_FORBIDDEN)
#             related_profile_obj = Cliente.objects.filter(profile=profile).first()
#         elif profile.tipo_usuario == 'domiciliario':
#             if campo_a_eliminar not in campos_permitidos_domiciliario:
#                 return Response({"detail": "No se puede eliminar este campo o no pertenece a tu tipo de usuario."}, status=status.HTTP_403_FORBIDDEN)
#             related_profile_obj = Domiciliario.objects.filter(profile=profile).first()
#         elif profile.tipo_usuario == 'tienda':
#             return Response({"detail": "Las tiendas no tienen campos eliminables de esta forma."}, status=status.HTTP_403_FORBIDDEN)
#         else:
#             return Response({"detail": "Tu tipo de usuario no permite eliminar campos de esta forma."}, status=status.HTTP_403_FORBIDDEN)

#         if related_profile_obj and hasattr(related_profile_obj, campo_a_eliminar):
#             setattr(related_profile_obj, campo_a_eliminar, None)
#             related_profile_obj.save()
#             return Response({"detail": f"El campo '{campo_a_eliminar}' ha sido eliminado exitosamente."}, status=status.HTTP_200_OK)
#         else:
#             return Response({"detail": "Campo no encontrado o no aplicable a tu perfil específico."}, status=status.HTTP_400_BAD_REQUEST)

# # Vistas de API para Productos


# #VIEWSET LISTA, ELIMINA, ACTUALIZA, CREA Y FILTRA PRODUCTOS
# class ProductosViewSet(viewsets.ModelViewSet):
#     queryset = Productos.objects.all().order_by('id') # Asegura un orden por defecto
#     serializer_class = ProductosSerializer
#     # Permite lectura a no autenticados, escritura a autenticados
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

#     def get_queryset(self):
#         queryset = super().get_queryset()
        
#         # Filtros de búsqueda
#         categoria_slug = self.request.query_params.get('categoria', None)
#         if categoria_slug:
#             queryset = queryset.filter(categoria__slug=categoria_slug)

#         tipo_mascota = self.request.query_params.get('tipo_mascota', None)
#         if tipo_mascota:
#             queryset = queryset.filter(tipo_mascota=tipo_mascota)
        
#         precio_min = self.request.query_params.get('precio_min', None)
#         if precio_min:
#             try:
#                 queryset = queryset.filter(precio__gte=float(precio_min))
#             except ValueError:
#                 pass # Ignorar valores inválidos

#         precio_max = self.request.query_params.get('precio_max', None)
#         if precio_max:
#             try:
#                 queryset = queryset.filter(precio__lte=float(precio_max))
#             except ValueError:
#                 pass

#         busqueda = self.request.query_params.get('busqueda', None)
#         if busqueda:
#             queryset = queryset.filter(
#                 Q(nombre__icontains=busqueda) |
#                 Q(description__icontains=busqueda)
#             )

#         orden = self.request.query_params.get('orden', None)
#         if orden:
#             queryset = queryset.order_by(orden)

#         return queryset

#     def perform_create(self, serializer):
#         # Asigna el usuario actual como el creador del producto
#         serializer.save(user=self.request.user)

#     # Acción personalizada para añadir una reseña a un producto
#     @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
#     def add_review(self, request, pk=None):
#         producto = self.get_object() # Obtiene el producto por su ID
#         # Asume que la reseña es enviada por el Cliente
#         if request.user.profile.tipo_usuario != 'cliente':
#             return Response({"detail": "Solo los clientes pueden añadir reseñas."}, status=status.HTTP_403_FORBIDDEN)

#         serializer = ResenaProductoMascotaSerializer(data=request.data)
#         if serializer.is_valid():
#             # Asigna el usuario autenticado y el producto a la reseña
#             serializer.save(user=request.user, producto=producto)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# #VIEWSET PARA CATEGORIAS DE MASCOTAS, SOLO LECTURA
# class CategoriaMascotaViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = CategoriaMascota.objects.all()
#     serializer_class = CategoriaMascotaSerializer
#     permission_classes = [permissions.AllowAny]

# #VIEWSET PARA GESTIONAR RESEÑAS DE PRODUCTOS, CREAR ACTUALIZAR Y ELIMINAR
# class ResenaProductoMascotaViewSet(viewsets.ModelViewSet):
#     queryset = ResenaProductoMascota.objects.all()
#     serializer_class = ResenaProductoMascotaSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Permite lectura a todos, escritura a autenticados

#     def perform_create(self, serializer):
#         # Asigna la reseña al usuario autenticado
#         if self.request.user.profile.tipo_usuario != 'cliente':
#             raise serializer.ValidationError({"detail": "Solo los clientes pueden crear reseñas."})
#         serializer.save(user=self.request.user)

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         # Permite filtrar reseñas por producto
#         producto_id = self.request.query_params.get('producto_id', None)
#         if producto_id:
#             queryset = queryset.filter(producto__id=producto_id)
#         return queryset

#     def get_permissions(self):
#         # Los usuarios solo pueden editar o eliminar sus propias reseñas
#         if self.action in ['update', 'partial_update', 'destroy']:
#             return [permissions.IsAuthenticated(), IsOwnerOfReview()]
#         return super().get_permissions()

# # Permiso personalizado para verificar si el usuario es el propietario de la reseña
# class IsOwnerOfReview(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         # Permiso de lectura permitido a cualquier solicitud.
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         # Permiso de escritura solo para el propietario de la reseña.
#         return obj.user == request.user
