from django import forms
from django.contrib.auth.models import User
from tasks.models import Cliente, Domiciliario, Profile, ResenaProductoMascota, Tienda, Direccion
from datetime import date
import re


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


# cuando el usuario se registra por primera vez


TIPO_USUARIO = (
    ('cliente', 'Cliente'),
    ('domiciliario', 'Domiciliario'),
    ('tienda', 'Tienda'),
)

class SignupForm(forms.Form):
    username = forms.CharField(max_length=150, help_text="Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.", required=True, label="Usuario")
    nombre = forms.CharField(max_length=200, required=True, label="Nombre")
    apellido = forms.CharField(max_length=200)
    correo = forms.EmailField(required=True)
    
    tipo_usuario = forms.ChoiceField(choices=TIPO_USUARIO, required=True, label="Tipo de Usuario") # Campo requerido

    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña", required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña", required=True)

    # Campos opcionales para Cliente, Domiciliario que aparecerán una vez ya ingrese
    segundo_apellido = forms.CharField(max_length=200, required=False)
    celular = forms.CharField(max_length=20, required=False)
    genero = forms.CharField(max_length=1, required=False)
    fecha_nacimiento = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}), # Esto ayuda a que el navegador muestre un selector de fecha
    ) 
        
    def clean_username(self):
        username = self.cleaned_data.get('username')

        # caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9@.+\-_]+$', username):
            raise forms.ValidationError("El usuario contiene caracteres no permitidos.")

        # nombres prohibidos
        restricted = ["admin", "root", "superuser", "test"]
        if username.lower() in restricted:
            raise forms.ValidationError("Este usuario no está permitido.")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")

        return username

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Profile.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return correo
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("La contraseña debe incluir al menos una letra mayúscula.")

        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("La contraseña debe incluir al menos una letra minúscula.")

        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("La contraseña debe incluir al menos un número.")

        if not re.search(r'[@$!%*#?&]', password):
            raise forms.ValidationError("La contraseña debe contener al menos un símbolo (@, $, !, %, *, #, ?, &).")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden")

        return cleaned_data


#el usuario podrá completar su información personal en el profile
class ProfileUpdateForm(forms.ModelForm):
    nombre = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Nombre")
    apellido = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Apellido")
    correo = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}), label="Correo Electrónico")
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Debes ser mayor de edad.'
    )
    segundo_apellido = forms.CharField(max_length=200, required=False)
    celular = forms.CharField(max_length=15, required=False)
    genero = forms.ChoiceField(choices=Profile.GENERO_OPCIONES, required=False)
    
    class Meta:
        model = Profile
        fields = ['nombre', 'apellido', 'correo',  'fecha_nacimiento']

    def __init__(self, *args, **kwargs):
        self.profile_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if not self.profile_instance:
            raise ValueError("Se necesita un perfil existente")
        
        self.role_specific_instance = None # para mantener la instancia de cliente y domiciliario

        if self.profile_instance.tipo_usuario == 'cliente':
            self.role_specific_instance, created = Cliente.objects.get_or_create(profile=self.profile_instance)
            if self.role_specific_instance:
                self.fields['segundo_apellido'].initial = self.role_specific_instance.segundo_apellido
                self.fields['celular'].initial = self.role_specific_instance.celular
                self.fields['genero'].initial = self.role_specific_instance.genero



        if self.profile_instance.tipo_usuario == 'tienda':
            self.fields.pop('segundo_apellido', None)
            self.fields.pop('celular', None)
            self.fields.pop('genero', None)

            self.role_specific_instance, created = Tienda.objects.get_or_create(profile=self.profile_instance)
            # Añadir campos específicos de tienda
            self.fields['nombre_tienda'] = forms.CharField(
                max_length=200, 
                required=False, 
                widget=forms.TextInput(attrs={'class': 'form-control'}), 
                label="Nombre de la Tienda"
            )
            self.fields['nit'] = forms.CharField(
                max_length=50, 
                required=False, 
                widget=forms.TextInput(attrs={'class': 'form-control'}), 
                label="NIT"
            )
            if self.role_specific_instance:
                self.fields['nombre_tienda'].initial = self.role_specific_instance.nombre_tienda
                self.fields['nit'].initial = self.role_specific_instance.nit
        

    def save(self, commit=True):

        profile = super().save(commit=False)
        
        profile.nombre = self.cleaned_data.get('nombre', profile.nombre)
        profile.apellido = self.cleaned_data.get('apellido', profile.apellido)
        profile.correo = self.cleaned_data.get('correo', profile.correo)
        profile.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento', profile.fecha_nacimiento)
    
        if commit:
            profile.save() # Guarda la instancia de Profile

            # Guarda los campos asociados a Cliente o Domiciliario según el tipo de usuario
            
            if self.role_specific_instance:
                if self.profile_instance.tipo_usuario == 'cliente':
                    self.role_specific_instance.segundo_apellido = self.cleaned_data.get('segundo_apellido', self.role_specific_instance.segundo_apellido)
                    self.role_specific_instance.celular = self.cleaned_data.get('celular', self.role_specific_instance.celular)
                    self.role_specific_instance.genero = self.cleaned_data.get('genero', self.role_specific_instance.genero)
                    self.role_specific_instance.save()

                elif self.profile_instance.tipo_usuario == 'tienda':
                    self.role_specific_instance.nombre_tienda = self.cleaned_data.get('nombre_tienda', self.role_specific_instance.nombre_tienda)
                    self.role_specific_instance.nit = self.cleaned_data.get('nit', self.role_specific_instance.nit)
                    self.role_specific_instance.save()
            
        return profile
        
    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18:
                raise forms.ValidationError('Debes ser mayor de edad para registrarte.')
        return fecha_nacimiento

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['nombre_quien_recibe', 'pais', 'departamento', 'ciudad', 'direccion', 'codigo_postal', 'info_adicional', 'telefono', 'es_predeterminada']
        