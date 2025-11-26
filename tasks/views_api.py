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
from django.contrib.gis.measure import D

#Geolocalización

from rest_framework.decorators import api_view, permission_classes
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import uuid

#serializadores
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
        ubicacion_recogida__distance_lte=(domiciliario_point, D(km=5))
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
