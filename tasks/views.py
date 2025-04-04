from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import ProductoForm, SignupForm
from django.db import IntegrityError
from .models import Productos, Profile
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': SignupForm()
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['usuario'], password=request.POST['password1'])
                user.save()

                # Crear perfil con los campos adicionales
                profile = Profile(
                    user=user,
                    nombre=request.POST['nombre'],
                    apellido=request.POST['apellido'],
                    correo=request.POST['correo']
                )
                profile.save()

                login(request, user)
                return redirect('productos')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': SignupForm(),
                    "error": '⚠️ El nombre de usuario ya existe.'
                })
        return render(request, 'signup.html', {
            'form': SignupForm(),
            "error": '❌ Las contraseñas no coinciden.'
        })

    
@login_required
def productos(request):
    productos = Productos.objects.filter(user=request.user)
    return render(request, 'productos.html', {'productos': productos})

@login_required
def producto_detail(request, producto_id):
    if request.method == 'GET':
        producto = get_object_or_404(Productos, pk=producto_id, user=request.user)

        form = ProductoForm(instance=producto)
        return render(request, 'producto_detail.html', {'producto': producto, 'form': form})
    else:
        try:
            producto = get_object_or_404(Productos, pk=producto_id, user=request.user)
            form = ProductoForm(request.POST, instance=producto)
            form.save()
            return redirect('productos')
        except ValueError:
            return render(request, 'producto_detail.html', {'producto': producto, 'form': form, 'error': "Error updating product"})
@login_required
def delete_producto(request, producto_id):
    producto = get_object_or_404(Productos, pk=producto_id, user=request.user)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
        'form': AuthenticationForm
    })
    else:
        user = authenticate(request, username=request.POST['usuario'], password=request.POST['password1'])
        
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'username or password is incorrect'
                })
        else:
            login(request, user)
            return redirect('productos')
        
