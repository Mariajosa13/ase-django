from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    correo = models.EmailField(null=True, blank=True)

    # campos opcionales que el usuario podrá editar

    segundo_apellido = models.CharField(max_length=200, blank=True, null=True)
    fecha_nacimiento = models.DateField(validators=[validar_mayor_edad], blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_OPCIONES, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - by {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Si es una instancia existente, verificamos que no se cambien los campos restringidos
        if self.pk:
            old_instance = Profile.objects.get(pk=self.pk)
            if old_instance.nombre != self.nombre:
                raise ValidationError("No se puede modificar el nombre.")
            if old_instance.apellido != self.apellido:
                raise ValidationError("No se puede modificar el primer apellido.")
            if old_instance.fecha_nacimiento and old_instance.fecha_nacimiento != self.fecha_nacimiento:
                raise ValidationError("No se puede modificar la fecha de nacimiento una vez establecida.")
                
        super(Profile, self).save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # se crear perfil de usuario
    if created:
        Profile.objects.create(
            user=instance,
            nombre="Usuario",  # Valores predeterminados
            apellido="Nuevo",
            correo=instance.email if instance.email else ""
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el perfil cuando se guarda el usuario."""
    if not hasattr(instance, 'profile'):
        Profile.objects.create(
            user=instance,
            nombre="Usuario",
            apellido="Nuevo",
            correo=instance.email if instance.email else ""
        )
    instance.profile.save()

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
    TIPO_MASCOTA_CHOICES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('ave', 'Ave'),
        ('pez', 'Pez'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(null=True, blank=True)
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
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='resenas')
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
