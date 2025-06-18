from django import forms
from django.contrib.auth.models import User
from tasks.models import Cliente, Domiciliario, Profile, ResenaProductoMascota
from datetime import date

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

    # Campos opcionales para Cliente, Domiciliario, Tienda que aparecerán una vez ya ingrese
    segundo_apellido = forms.CharField(max_length=200, required=False)
    celular = forms.CharField(max_length=20, required=False)
    genero = forms.CharField(max_length=1, required=False)
    fecha_nacimiento = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}), # Esto ayuda a que el navegador muestre un selector de fecha
    ) 

    vehiculo = forms.CharField(max_length=100, required=False)
    nombre_tienda = forms.CharField(max_length=200, required=False)
    nit = forms.CharField(max_length=50, required=False)
        
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if Profile.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return correo

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden")

        return cleaned_data


#el usuario podrá completar su información personal en el profile
class ProfileUpdateForm(forms.ModelForm):
    nombre = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Nombre")
    segundo_apellido = forms.CharField(max_length=200, required=False)
    correo = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}), label="Correo Electrónico")
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Debes ser mayor de edad.'
    )
    celular = forms.CharField(max_length=15, required=False)
    genero = forms.ChoiceField(choices=Profile.GENERO_OPCIONES, required=False)
    
    class Meta:
        model = Profile
        fields = ['nombre', 'segundo_apellido', 'correo',  'fecha_nacimiento', 'celular', 'genero']

    def __init__(self, *args, **kwargs):
        self.profile_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if not self.profile_instance:
            raise ValueError("Se necesita un perfil existente")
        
        self.role_specific_instance = None # para mantener la instancia de cliente y domiciliario

        if self.profile_instance.tipo_usuario == 'cliente':
            self.role_specific_instance, created = Cliente.objects.get_or_create(profile=self.profile_instance)

        elif self.profile_instance.tipo_usuario == 'domiciliario':
            self.role_specific_instance, created = Domiciliario.objects.get_or_create(profile=self.profile_instance)

            self.fields['vehiculo'] = forms.CharField(
                max_length=50, 
                required=False, 
                widget=forms.TextInput(attrs={'class': 'form-control'}), 
                label="Placa del Vehículo"
            )

            if self.role_specific_instance:
                self.fields['vehiculo'].initial = self.role_specific_instance.vehiculo

    def save(self, commit=True):

        profile = super().save(commit=False)
        
        profile.nombre = self.cleaned_data.get('nombre', profile.nombre)
        profile.apellido = self.cleaned_data.get('apellido', profile.apellido)
        profile.correo = self.cleaned_data.get('correo', profile.correo)
        profile.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento', profile.fecha_nacimiento)
        profile.genero = self.cleaned_data.get('genero', profile.genero)
        profile.celular = self.cleaned_data.get('celular', profile.celular)
        profile.segundo_apellido = self.cleaned_data.get('segundo apellido', profile.segundo_apellido)

        if commit:
            profile.save() # Guarda la instancia de Profile

            # Guarda los campos asociados a Cliente o Domiciliario según el tipo de usuario
            
        elif self.profile_instance.tipo_usuario == 'domiciliario' and self.role_specific_instance:
                self.role_specific_instance.vehiculo = self.cleaned_data.get('vehiculo')
            
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
