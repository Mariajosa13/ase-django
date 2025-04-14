from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    correo = models.EmailField(null=True, blank=True)

    def _str_(self):
        return f"{self.nombre} - by {self.user.username}"
    
 
 # Productos Claude
    

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
        return reverse('producto_mascota_detalle', kwargs={'slug': self.slug})

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
