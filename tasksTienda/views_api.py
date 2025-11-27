import secrets
from rest_framework import status, permissions
from rest_framework.response import Response
from django.contrib.gis.measure import D
from django.contrib.auth.models import AnonymousUser
from .authentication import ApiKeyAuthBackend

#Geolocalización

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import uuid

# Importa los modelos generales de 'tasks'
from tasks.models import Profile, ApiKey

from .serializers import (
    ProductoSerializer
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_api_key(request):
    profile = request.user.profile
    if profile.tipo_usuario != 'tienda':
        return Response({'error': 'Solo las tiendas pueden obtener una API Key'}, status=status.HTTP_403_FORBIDDEN)
    api_key_obj, created = ApiKey.objects.get_or_create(profile=profile)

    tienda_nombre = getattr(profile, 'tienda', None).nombre_tienda if hasattr(profile, 'tienda') else profile.user.username

    return Response({
        'tienda': tienda_nombre,
        'api_key': str(api_key_obj.key)
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([ApiKeyAuthBackend]) 
@permission_classes([permissions.AllowAny]) #usa el permiso de API Key
def recibir_producto(request):
    #si pasa el permiso, request.profile y request.user contienen la información de la tienda.
    
    profile = request.profile # Profile de la tienda autenticada

    print("--- Contenido de request.data (incluye Archivos) ---")
    print(request.data)
    print("--- Contenido de request.FILES (solo Archivos) ---")
    print(request.FILES)
    print("-----------------------------------------------------")
    
    # Pasar el profile al serializador para la asignación de FKs
    serializer = ProductoSerializer(data=request.data, context={'request': request, 'profile': profile})
    
    if serializer.is_valid():
        producto = serializer.save()
        return Response({
            'message': 'Producto recibido exitosamente', 
            'producto_id': producto.id, 
            'tienda': profile.user.username
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generar_codigo():
    # Asegura un código de 6 dígitos con ceros iniciales
    return f"{secrets.randbelow(1000000):06d}"

    # pedido.codigo_entrega_tienda = generar_codigo()
    # pedido.codigo_recepcion_cliente = generar_codigo()
    # pedido.save()
