from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Productos(models.Model):
    nombre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    precio = models.BigIntegerField()
    fechaVencimiento = models.DateField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre + '- by ' + self.user.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    correo = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.nombre + '- by ' + self.user.username

