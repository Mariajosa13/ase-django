from django.forms import ModelForm
from .models import Productos, Profile


class ProductoForm(ModelForm):
    class Meta:
        model = Productos
        fields = ['nombre', 'description', 'precio']

class SignupForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['nombre', 'apellido', 'fechaNacimiento']
