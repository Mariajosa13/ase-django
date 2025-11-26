from django import forms
from django.contrib.auth.models import User
from tasks.models import Productos, CategoriaMascota, Tienda, ApiKey
from django.db import transaction
import uuid
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.forms import OSMWidget, PointField




#registro e ingreso tienda

TIPO_USUARIO = (
    ('cliente', 'Cliente'),
    ('domiciliario', 'Domiciliario'),
    ('tienda', 'Tienda'),
)

class SignupFormTienda(forms.ModelForm):
    correo = forms.EmailField(required=True, label="Correo Electrónico")
    password1 = forms.CharField(label="Contraseña", min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar Contraseña", widget=forms.PasswordInput)

    tipo_usuario = forms.ChoiceField(
        choices=[('tienda', 'Tienda')], 
        required=True, 
        initial='tienda',
        widget=forms.HiddenInput()
    )

    ubicacion = forms.CharField(
    required=True,
    label="Ubicación (Ciudad)",
    widget=forms.TextInput(attrs={
        "placeholder": "Ej: Medellín, Antioquia",
    })
)

    class Meta:
        model = Tienda
        fields = ['nombre_tienda', 'nit', 'ubicacion']

    def clean_nombre_tienda(self):
        nombre_tienda = self.cleaned_data['nombre_tienda']
        if User.objects.filter(username=nombre_tienda).exists():
            raise forms.ValidationError("Este nombre de tienda ya está en uso.")
        return nombre_tienda

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            user = User.objects.create_user(
                username=self.cleaned_data['nombre_tienda'],
                password=self.cleaned_data['password1']
            )

            profile = user.profile
            profile.tipo_usuario = 'tienda'
            profile.correo = self.cleaned_data['correo']
            profile.save()

            tienda_instance = super().save(commit=False)
            tienda_instance.profile = profile  
            tienda_instance.save()

            api_key_obj = ApiKey.objects.create(
                tienda=tienda_instance 
            )

            return user, api_key_obj.key

# formulario para crear o editar un producto
class ProductoForm(forms.ModelForm): #el modelForm esta directamente conectado a la base de datos django
    class Meta:
        model = Productos
        fields = ['nombre', 'description', 'precio', 'stock', 'imagen', 'categoria', 'tipo_mascota', 'destacado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}), #para que se vea mas bonito
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tipo_mascota': forms.Select(attrs={'class': 'form-select'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    tipo_mascota = forms.ChoiceField(
        choices=Productos.TIPO_MASCOTA_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
            })
    )

#Este formulario se usa para filtrar los productos en las vistas como: productos por categoría, todos los productos
class FiltroProductoMascotaForm(forms.ModelForm):
   ORDEN_CHOICES = [
      ('', 'Ordenar por'),
      ('precio', 'Precio (menor a mayor)'),
      ('-precio', 'Precio (mayor a menor)'),
      ('nombre', 'Nombre (A-Z)'),
      ('-nombre', 'Nombre (Z-A)'),
      ('-created', 'Más recientes'),
 ]
   busqueda = forms.CharField(required=False, widget=forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'Buscar productos...'
 }))
   categoria = forms.ModelChoiceField(
       queryset=CategoriaMascota.objects.all(), 
       required=False, 
       empty_label="Todas las categorías", 
       widget=forms.Select(attrs={
           'class': 'form-select'
           })
)
   tipo_mascota = forms.ChoiceField(
       choices=[('', 'Todas las mascotas')] + Productos.TIPO_MASCOTA_CHOICES,
       required=False, 
       widget=forms.Select(attrs={
           'class': 'form-select'
           })
)
   precio_min = forms.IntegerField(
       required=False, 
       min_value=0, 
       widget=forms.NumberInput(attrs={
           'class': 'form-control', 
           'placeholder': 'Precio mínimo'
           })
)
   precio_max = forms.IntegerField(
       required=False, 
       min_value=0, 
       widget=forms.NumberInput(attrs={
           'class': 'form-control',
           'placeholder': 'Precio máximo'
           })
)
   orden = forms.ChoiceField(choices=ORDEN_CHOICES, 
        required=False, 
        widget=forms.Select(attrs={
            'class': 'form-select'
            })
)
