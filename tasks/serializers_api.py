from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg, Q
from django.db import IntegrityError
from .models import Profile, CategoriaMascota, Productos, ResenaProductoMascota, Cliente, Domiciliario, Tienda
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'username', 'tipo_usuario', 'nombre', 'apellido', 'correo', 'fecha_nacimiento']
        read_only_fields = ['tipo_usuario', 'user']

# Serializers específicos para CADA ROL para cuando se muestre el detalle del perfil
class ClienteSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['segundo_apellido', 'celular', 'genero']

class DomiciliarioSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domiciliario
        fields = ['vehiculo', 'segundo_apellido', 'celular', 'genero']

class TiendaSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = ['nombre_tienda', 'nit']

class SignupAPISerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    nombre = serializers.CharField(max_length=200)
    apellido = serializers.CharField(max_length=200)
    correo = serializers.EmailField()
    tipo_usuario = serializers.ChoiceField(choices=Profile.TIPO_USUARIO_CHOICES)

    # Campos opcionales que pueden venir en la solicitud, mapeados a los subtipos
    # Estos campos se usarán para cualquier tipo de usuario que los necesite
    segundo_apellido = serializers.CharField(max_length=200, required=False, allow_blank=True)
    celular = serializers.CharField(max_length=20, required=False, allow_blank=True)
    genero = serializers.CharField(max_length=1, required=False, allow_blank=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    vehiculo = serializers.CharField(max_length=100, required=False, allow_blank=True)
    nombre_tienda = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nit = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Este nombre de usuario ya está en uso."})
        if Profile.objects.filter(correo=data['correo']).exists():
            raise serializers.ValidationError({"correo": "Este correo electrónico ya está registrado."})
            
        # Validación de mayor debe estar accesible
        fecha_nacimiento = data.get('fecha_nacimiento')
        if fecha_nacimiento:
            from datetime import date
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18:
                raise serializers.ValidationError({"fecha_nacimiento": "Debes ser mayor de edad para registrarte."})
                
        return data

def create(self, validated_data):
        try:
            # Crear el usuario base de Django
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password']
            )

            # Crear el perfil general (los campos que aplican a todos)
            profile = Profile.objects.create(
                user=user,
                nombre=validated_data['nombre'],
                apellido=validated_data['apellido'],
                correo=validated_data['correo'],
                tipo_usuario=validated_data['tipo_usuario'],
                fecha_nacimiento=validated_data.get('fecha_nacimiento')
            )

            # Crear la instancia del tipo de usuario específico
            tipo_usuario = validated_data['tipo_usuario']
            if tipo_usuario == 'cliente':
                Cliente.objects.create(
                    profile=profile,
                    segundo_apellido=validated_data.get('segundo_apellido', ''),
                    celular=validated_data.get('celular', ''),
                    genero=validated_data.get('genero', 'N')
                )
            elif tipo_usuario == 'domiciliario':
                Domiciliario.objects.create(
                    profile=profile,
                    vehiculo=validated_data.get('vehiculo', ''),
                    segundo_apellido=validated_data.get('segundo_apellido', ''),
                    celular=validated_data.get('celular', ''),
                    genero=validated_data.get('genero', 'N')
                )
            elif tipo_usuario == 'tienda':
                Tienda.objects.create(
                    profile=profile,
                    nombre_tienda=validated_data.get('nombre_tienda', ''),
                    nit=validated_data.get('nit', '')
                )
            return user
        except IntegrityError:
            raise serializers.ValidationError({"detail": "Error de base de datos: el nombre de usuario o correo ya existen."})
        except Exception as e:
            # Esto atrapará errores inesperados durante la creación de los subtipos
            raise serializers.ValidationError({"detail": f"Ocurrió un error inesperado durante el registro: {e}"})

# Jason Web token serializer para obtener el token JWT con datos del usuario, valida que las credenciales sean correctas y si son correctas, devuelve un token JWT con datos del usuario, se hace personalizado para incluir datos del perfil del usuario y el user_type para que el frontend pueda identificar el tipo de usuario y mostrar la información correspondiente.
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        try:
            profile = Profile.objects.get(user=user)
            token['user_type'] = profile.tipo_usuario
            token['username'] = user.username
            token['email'] = user.email
            token['profile_id'] = profile.id
            token['nombre'] = profile.nombre
            token['apellido'] = profile.apellido
        except Profile.DoesNotExist:
            token['user_type'] = 'unknown'
        return token
    
# SERIALIZERS DE PRODUCTOS
    
class CategoriaMascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaMascota
        fields = ['id', 'nombre', 'slug', 'imagen']
        read_only_fields = ['slug'] # El slug se genera automáticamente

class ResenaProductoMascotaSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True) # Nombre del usuario de la reseña

    class Meta:
        model = ResenaProductoMascota
        fields = ['id', 'producto', 'user', 'user_username', 'calificacion', 'comentario', 'fecha_creacion']
        read_only_fields = ['user', 'producto', 'fecha_creacion'] # Se asignan en la vista

class ProductosSerializer(serializers.ModelSerializer):
    categoria = CategoriaMascotaSerializer(read_only=True) # Muestra los detalles de la categoría
    # Campo para escribir el ID de la categoría al crear/actualizar (solo aplica para funciones de la API)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaMascota.objects.all(), source='categoria', write_only=True, required=False, allow_null=True
    )
    
    # Campo para obtener el promedio de calificaciones (Solo aplica para funciones de la API)
    promedio_calificacion = serializers.SerializerMethodField()
    # Para mostrar las reseñas anidadas (solo lectura)
    resenas = ResenaProductoMascotaSerializer(many=True, read_only=True) 

    class Meta:
        model = Productos
        fields = [
            'id', 'nombre', 'description', 'precio', 'stock', 'slug', 'imagen', 
            'categoria', 'categoria_id', 'tipo_mascota', 'destacado', 'fechaVencimiento', 'created', 
            'important', 'user', 'promedio_calificacion', 'resenas'
        ]
        read_only_fields = ['user', 'slug', 'created', 'fechaVencimiento'] # Campos generados automáticamente

    def get_promedio_calificacion(self, obj):
        if hasattr(obj, 'resenas_producto_mascota'):
            avg_rating = obj.resenas_producto_mascota.aggregate(Avg('calificacion'))['calificacion__avg']
            return round(avg_rating, 2) if avg_rating is not None else 0.0
        return 0.0