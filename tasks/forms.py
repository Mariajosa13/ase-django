from django import forms
from .models import Productos, Profile, ResenaProductoMascota, CategoriaMascota


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['nombre', 'description', 'precio', 'stock', 'imagen', 'categoria', 'tipo_mascota', 'destacado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
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
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class ResenaProductoMascotaForm(forms.ModelForm):
   class Meta:
      model = ResenaProductoMascota
      fields = ['calificacion', 'comentario']
      widgets = {
         'calificacion': forms.Select(attrs={'class': 'form-select'}),
         'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
 }

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
   categoria = forms.ModelChoiceField(queryset=CategoriaMascota.objects.all(), required=False, empty_label="Todas las categorías", widget=forms.Select(attrs={'class': 'form-select'})
)
   tipo_mascota = forms.ChoiceField(choices=[('', 'Todas las mascotas')] + Productos.TIPO_MASCOTA_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'})
)
   precio_min = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio mínimo'})
)
   precio_max = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio máximo'})
)
   orden = forms.ChoiceField(choices=ORDEN_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'})
)

class SignupForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nombre', 'apellido', 'correo']
