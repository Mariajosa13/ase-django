from urllib import request
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.gis.db import models as gis_models

# SECCIÓN USUARIOS


def validar_mayor_edad(fecha_nacimiento):
    #validacion mayor de edad
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    if edad < 18:
        raise ValidationError('Debes ser mayor de edad para registrarte.')

class Profile(models.Model):
    GENERO_OPCIONES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decirlo'),
    ]

    TIPO_USUARIO_CHOICES = [ # Cambiado a TIPO_USUARIO_CHOICES para evitar conflicto de nombre con la tupla global
        ('cliente', 'Cliente'),
        ('domiciliario', 'Domiciliario'),
        ('tienda', 'Tienda'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='cliente') # Establece un valor predeterminado
    nombre = models.CharField(max_length=200, blank=True, null=True) # Permitir null y blank para creación inicial
    apellido = models.CharField(max_length=200, blank=True, null=True) # Permitir null y blank para creación inicial
    correo = models.EmailField(null=True, blank=True, unique=True)
    fecha_nacimiento = models.DateField(validators=[validar_mayor_edad], blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - by {self.user.username}" # Usar user.username para mejor descripción
    
    def save(self, *args, **kwargs):
        # Si es una instancia existente, verificamos que no se cambien los campos restringidos
        # Solo se restringe cambiar nombre y apellido una vez establecidos, no fecha_nacimiento
        # ya que el ProfileUpdateForm lo maneja.
        if self.pk:
            old_instance = Profile.objects.get(pk=self.pk)
            if old_instance.nombre and old_instance.nombre != self.nombre:
                raise ValidationError("No se puede modificar el nombre.")
            if old_instance.apellido and old_instance.apellido != self.apellido:
                raise ValidationError("No se puede modificar el primer apellido.")
            # Eliminada la validación para fecha_nacimiento para permitir actualización desde ProfileUpdateForm
        super(Profile, self).save(*args, **kwargs)

# Señal para crear un perfil cuando se crea un usuario.
# Ahora crea un perfil con campos vacíos que serán llenados por la vista.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) # Crea un perfil vacío, la vista lo llenará

class Cliente(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    # info que podrá agregar el cliente
    segundo_apellido = models.CharField(max_length=200, blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)
    genero = models.CharField(max_length=1, choices=Profile.GENERO_OPCIONES, default='N')
    
    def __str__(self):
        return f"Cliente: {self.profile.user.username}"
 
class Domiciliario(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    vehiculo = models.CharField(max_length=50, blank=True, null=True)
    segundo_apellido = models.CharField(max_length=200, blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)
    genero = models.CharField(max_length=1, choices=Profile.GENERO_OPCIONES, default='N')

    documento_frontal = models.FileField(upload_to='domiciliario/documentos/identidad/', blank=True, null=True)
    documento_trasera = models.FileField(upload_to='domiciliario/documentos/identidad/', blank=True, null=True)
    licencia_conducir = models.FileField(upload_to='domiciliario/documentos/licencias/', blank=True, null=True)
    tarjeta_propiedad = models.FileField(upload_to='domiciliario/documentos/propiedad/', blank=True, null=True)
    soat = models.FileField(upload_to='domiciliario/documentos/soat/', blank=True, null=True)
    foto_perfil_domiciliario = models.ImageField(upload_to='domiciliario/perfiles/', blank=True, null=True)

    ESTADO_VERIFICACION_CHOICES = [
        ('PENDIENTE_DOCUMENTOS', 'Pendiente de carga de documentos'),
        ('EN_REVISION', 'En revisión'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    estado_verificacion = models.CharField(max_length=30, choices=ESTADO_VERIFICACION_CHOICES, default='PENDIENTE_DOCUMENTOS')

    def __str__(self):
        return f"Domiciliario: {self.profile.user.username}"

class ApiKey(models.Model):
    tienda = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'TIPO_USUARIOS_CHOICES':'tienda'})
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

class Tienda(gis_models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    nombre_tienda = models.CharField(max_length=200, blank=True, null=True)
    nit = models.CharField(max_length=50, blank=True, null=True)
    ubicacion = gis_models.PointField(null=True, blank=True, srid=4326) # sistema de coordenadas estandar Lat Lng


    def __str__(self):
        return f"Tienda: {self.profile.user.username} ({self.nombre_tienda})"

@receiver(post_save, sender=Profile)
def crear_subtipo_usuario(sender, instance, created, **kwargs):
    if created and instance.tipo_usuario:
        if instance.tipo_usuario == 'cliente':
            Cliente.objects.create(profile=instance)
        elif instance.tipo_usuario == 'domiciliario':
            Domiciliario.objects.create(profile=instance)
        elif instance.tipo_usuario == 'tienda':
            Tienda.objects.create(profile=instance)

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    domiciliario_asignado = models.ForeignKey(Domiciliario, on_delete=models.SET_NULL, null=True, blank=True)
    ubicacion_recogida = gis_models.PointField(srid=4326) 
    ubicacion_entrega = gis_models.PointField(srid=4326)

    ESTADOS = [
        ('DISPONIBLE', 'Esperando domiciliario'),
        ('EN_CURSO', 'Asignado, en camino a recoger'),
        ('EN_CAMINO', 'Recogido, en camino a entregar'),
        ('ENTREGADO', 'Completado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='DISPONIBLE')
    codigo_entrega_tienda = models.CharField(max_length=6, null=True, blank=True, unique=True)
    codigo_recepcion_cliente = models.CharField(max_length=6, null=True, blank=True, unique=True)
    
class Direccion(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    nombre_quien_recibe = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, default='Colombia')
    departamento = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    info_adicional = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_predeterminada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.direccion}, {self.ciudad} - by {self.profile.user.username}"

# SECCIÓN MASCOTAS

class CategoriaMascota(models.Model):
   nombre = models.CharField(max_length=100)
   slug = models.SlugField(unique=True, blank=True)
   imagen = models.ImageField(upload_to='categorias_mascotas/', blank=True, null=True)
   
   
   def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
         
        def __str__(self):
            return self.nombre

class Meta:
    verbose_name_plural = "Categorías de Mascotas"

class Productos(models.Model):
    tienda = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'TIPO_USUARIOS_CHOICES': 'tienda'})
    TIPO_MASCOTA_CHOICES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    precio = models.BigIntegerField()
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey(CategoriaMascota, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_mascota = models.CharField(max_length=10, choices=TIPO_MASCOTA_CHOICES, null=True, blank=True)
    destacado = models.BooleanField(default=False)
    fechaVencimiento = models.DateField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    important = models.BooleanField(default=False)
    datos_extra = models.JSONField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_mascota_display()} - by {self.user.username}"

    def get_absolute_url(self):
        return reverse('producto_detail', args=[str(self.id)])

class Meta:
    verbose_name = "Producto para Mascota"
    verbose_name_plural = "Productos para Mascotas"
   
class ResenaProductoMascota(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='resenas_producto_mascota')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        unique_together = ('producto', 'usuario')
        verbose_name = "Reseña de Producto"
        verbose_name_plural = "Reseñas de Productos"
    
    def __str__(self):
        return f'Reseña de {self.usuario.username} para {self.producto.nombre}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True) # permite que los productos queden en el carrito aunque el usuario no esté logueado
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        return f"Carrito (Sesión: {self.session_key[:10]}...)"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.producto.nombre} en Carrito de {self.cart}"

    def get_total_price(self):
        return self.quantity * self.producto.precio