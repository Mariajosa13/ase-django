from django import forms
from django.contrib.auth.models import User
from ..tasks.models import Productos, Profile, ResenaProductoMascota, CategoriaMascota
from datetime import date


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
