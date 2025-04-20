from django import forms
from django.contrib.auth.models import User
from .models import Productos, Profile, ResenaProductoMascota, CategoriaMascota
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

#para dejar reseña 
class ResenaProductoMascotaForm(forms.ModelForm):
   class Meta:
      model = ResenaProductoMascota
      fields = ['calificacion', 'comentario']
      widgets = {
         'calificacion': forms.Select(attrs={
             'class': 'form-select'
             }),
         'comentario': forms.Textarea(attrs={
             'class': 'form-control',
               'rows': 4
               }),
 }

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

# cuando el usuario se registra por primera vez
class SignupForm(forms.ModelForm):
    usuario = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cual es tu usuario'
        })
    )
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu nombre'
        })
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu apellido'
        })
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu correo electrónico'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        strip=False, #si el usuario ingresa un espacio se guarda como si hiciera parte de la contraseña
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['nombre', 'apellido', 'correo']


#el usuario podrá completar su información personal en el profile
class ProfileUpdateForm(forms.ModelForm):
    segundo_apellido = forms.CharField(max_length=200, required=False)
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Debes ser mayor de edad.'
    )
    celular = forms.CharField(max_length=15, required=False)
    genero = forms.ChoiceField(choices=Profile.GENERO_OPCIONES, required=False)
    
    class Meta:
        model = Profile
        fields = ['segundo_apellido', 'fecha_nacimiento', 'celular', 'genero']
        
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18:
                raise forms.ValidationError('Debes ser mayor de edad para registrarte.')
        return fecha_nacimiento
