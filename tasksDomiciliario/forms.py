from django import forms
from tasks.models import Domiciliario

class DomiciliarioProfileYDocumentos(forms.ModelForm):
    segundo_apellido = forms.CharField(max_length=200, required=False, label="Segundo Apellido")
    celular = forms.CharField(max_length=15, required=False, label="Número de Celular")
    genero = forms.ChoiceField(choices=Domiciliario.profile.field.related_model.GENERO_OPCIONES, required=False, label="Género") # Accessing choices from Profile model
    vehiculo = forms.CharField(max_length=50, required=False, label="Tipo de Vehículo (Ej. Moto, Carro)")

    documento_frontal = forms.FileField(
        label="Documento de Identidad (Frente)",
        required=True, # Make it required for submission
        help_text="Sube una imagen clara de la parte frontal de tu documento de identidad."
    )
    documento_trasera = forms.FileField(
        label="Documento de Identidad (Parte Posterior)",
        required=True,
        help_text="Sube una imagen clara de la parte posterior de tu documento de identidad."
    )
    licencia_conducir = forms.FileField(
        label="Licencia de Conducir",
        required=True,
        help_text="Sube una imagen clara de tu licencia de conducir vigente."
    )
    tarjeta_propiedad = forms.FileField(
        label="Tarjeta de Propiedad del Vehículo",
        required=True,
        help_text="Sube una imagen clara de la tarjeta de propiedad de tu vehículo."
    )
    soat = forms.FileField(
        label="SOAT",
        required=True,
        help_text="Sube una imagen o PDF de tu SOAT vigente."
    )
    foto_perfil_domiciliario = forms.ImageField(
        label="Foto de Perfil (Domiciliario)",
        required=True,
        help_text="Sube una foto clara de tu rostro."
    )

    class Meta:
        model = Domiciliario
        fields = [
            'segundo_apellido', 'celular', 'genero', 'vehiculo',
            'documento_frontal', 'documento_trasera', 
            'licencia_conducir', 'tarjeta_propiedad', 'soat', 
            'foto_perfil_domiciliario',
        ]
        widgets = {
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'genero': forms.Select(attrs={'class': 'form-control'}),
            'vehiculo': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_frontal': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'documento_trasera': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'licencia_conducir': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'tarjeta_propiedad': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'soat': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'foto_perfil_domiciliario': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_documento_frontal(self):
        doc_frontal = self.cleaned_data.get('documento_frontal')
        if doc_frontal:
            if not doc_frontal:
                raise forms.ValidationError("El documento es obligatorio.")
            if doc_frontal.size > 5 * 1024 * 1024: # 5MB
                raise forms.ValidationError("El archivo no puede exceder los 5MB.")
            if not doc_frontal.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                raise forms.ValidationError("Solo se permiten archivos PNG, JPG, JPEG o PDF.")
        return doc_frontal
    
    def clean_documento_trasera(self):
        doc_trasera = self.cleaned_data.get('documento_trasera')
        if doc_trasera:
            if not doc_trasera:
                raise forms.ValidationError("El documento es obligatorio.")
            if doc_trasera.size > 5 * 1024 * 1024: # 5MB
                raise forms.ValidationError("El archivo no puede exceder los 5MB.")
            if not doc_trasera.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                raise forms.ValidationError("Solo se permiten archivos PNG, JPG, JPEG o PDF.")
        return doc_trasera
    
    def clean_licencia_conducir(self):
        licencia = self.cleaned_data.get('licencia_conducir')
        if not licencia:
            raise forms.ValidationError("La licencia de conducir es obligatoria.")
        if licencia.size > 5 * 1024 * 1024:
            raise forms.ValidationError("El archivo no puede exceder los 5MB.")
        if not licencia.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            raise forms.ValidationError("Solo se permiten archivos PNG, JPG, JPEG o PDF.")
        return licencia
    
    def clean_tarjeta_propiedad(self):
        tarjeta = self.cleaned_data.get('tarejeta_propiedad')
        if not tarjeta:
            raise forms.ValidationError("La tarejeta de propiedad es obligatoria.")
        if tarjeta.size > 5 * 1024 * 1024:
            raise forms.ValidationError("El archivo no puede exceder los 5MB.")
        if not tarjeta.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            raise forms.ValidationError("Solo se permiten archivos PNG, JPG, JPEG o PDF.")
        return tarjeta
    
    def clean_soat(self):
        soat = self.cleaned_data.get('soat')
        if not soat:
            raise forms.ValidationError("El soat es obligatorio.")
        if soat.size > 5 * 1024 * 1024:
            raise forms.ValidationError("El archivo no puede exceder los 5MB.")
        if not soat.name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            raise forms.ValidationError("Solo se permiten archivos PNG, JPG, JPEG o PDF.")
        return soat