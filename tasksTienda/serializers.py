from datetime import date
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg, Q
from django.db import IntegrityError
from tasks.models import CategoriaMascota, Productos
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

#Geolocalización
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from django.contrib.gis.measure import D

class ProductoSerializer(serializers.ModelSerializer):
    tienda = serializers.StringRelatedField(read_only=True) #mostrará el __str__ del Profile
    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaMascota.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Productos
        fields = [
            'id', 'tienda', 'nombre', 'description', 'precio', 'stock', 
            'imagen', 'categoria', 'tipo_mascota', 'destacado', 
            'fechaVencimiento', 'created', 'important', 'datos_extra', 'user',
        ]
        read_only_fields = ['id', 'created', 'tienda', 'user']

    def create(self, validated_data):
        """Crea el producto asignando automáticamente el Profile y User de la tienda
        autenticada por API Key."""
        #obtenemos el Profile de la tienda en el contexto por la vista
        profile = self.context.get('profile') 
        
        if not profile:
            #esto maneja el caso de que la vista no haya inyectado el Profile.
            raise serializers.ValidationError("Error de autenticación o contexto: El perfil de la tienda no se pudo obtener.")

        #asignar el Profile de la tienda al campo 'tienda' del modelo Productos
        validated_data['tienda'] = profile
        
        #asignar el User de Django al campo 'user' del modelo Productos
        validated_data['user'] = profile.user 

        #crear y guardar la instancia del Producto
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Error al guardar el producto: {e}")