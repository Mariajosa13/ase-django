from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.core.paginator import Paginator
from .models import Productos, Profile, CategoriaMascota, ResenaProductoMascota
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .forms import ResenaProductoMascotaForm, FiltroProductoMascotaForm, ProductoForm, SignupForm


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

def productos(request):
    productos = Productos.objects.filter(user=request.user)
    return render(request, 'productos.html', {'productos': productos})

def lista_productos_mascotas(request):
    form = FiltroProductoMascotaForm(request.GET)
    productos = Productos.objects.all()

 # Aplicar filtros si el formulario es válido
    if form.is_valid():
 # Filtrar por categoría
        if form.cleaned_data.get('categoria'):
            productos = productos.filter(categoria=form.cleaned_data['categoria'])

 # Filtrar por tipo de mascota
        if form.cleaned_data.get('tipo_mascota'):
            productos = productos.filter(tipo_mascota=form.cleaned_data['tipo_mascota'])

 # Filtrar por rango de precio
        if form.cleaned_data.get('precio_min'):
            productos = productos.filter(precio__gte=form.cleaned_data['precio_min'])

        if form.cleaned_data.get('precio_max'):
            productos = productos.filter(precio__lte=form.cleaned_data['precio_max'])

 # Buscar por texto
        if form.cleaned_data.get('busqueda'):
            busqueda = form.cleaned_data['busqueda']
            productos = productos.filter(
                Q(nombre__icontains=busqueda) |
                Q(description__icontains=busqueda)
 )

 # Ordenar resultados
        if form.cleaned_data.get('orden'):
            productos = productos.order_by(form.cleaned_data['orden'])

 # Paginación
        paginator = Paginator(productos, 12) # 12 productos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categorias = CategoriaMascota.objects.all()

        context = {
            'form': form,
            'page_obj': page_obj,
            'productos': page_obj,
            'categorias': categorias,
}
    return render(request, 'productos/lista_productos_mascotas.html', context)

@login_required
def agregar_resena(request, slug):
    producto = get_object_or_404(Productos, slug=slug)

    if request.method == 'POST':
        form = ResenaProductoMascotaForm(request.POST)
        if form.is_valid():
            reseña = form.save(commit=False)
            reseña.producto = producto
            reseña.usuario = request.user
            reseña.save()
            return redirect('producto_mascota_detalle', slug=producto.slug)
    else:
        form = ResenaProductoMascotaForm()

    return render(request, 'agregar_resena.html', {
        'form': form,
        'producto': producto
    })

@login_required
def producto_detail(request, producto_id=None, slug=None):
    # Determina qué identificador se está utilizando
    if producto_id:
        producto = get_object_or_404(Productos, pk=producto_id, user=request.user)
    elif slug:
        producto = get_object_or_404(Productos, slug=slug)
    else:
        return HttpResponseBadRequest("No se proporcionó un identificador de producto")
    
    # Obtener reseñas, calificaciones y productos relacionados
    resenas = producto.resenas.all().order_by('-fecha_creacion') if hasattr(producto, 'resenas') else None
    promedio_calificacion = producto.resenas.aggregate(Avg('calificacion'))['calificacion__avg'] if hasattr(producto, 'resenas') else None
    
    # Productos relacionados (misma categoría)
    if hasattr(producto, 'categoria'):
        productos_relacionados = Productos.objects.filter(
            categoria=producto.categoria
        ).exclude(id=producto.id)[:4]
    else:
        productos_relacionados = None
    
    # Manejo de formularios
    if request.method == 'GET':
        form = ProductoForm(instance=producto)
        form_resena = ResenaProductoMascotaForm() if hasattr(producto, 'resenas') else None
    else:  # POST
        try:
            form = ProductoForm(request.POST, instance=producto)
            form.save()
            return redirect('productos')
        except ValueError:
            form_resena = ResenaProductoMascotaForm() if hasattr(producto, 'resenas') else None
            return render(request, 'producto_detail.html', {
                'producto': producto, 
                'form': form,
                'resenas': resenas,
                'promedio_calificacion': promedio_calificacion,
                'productos_relacionados': productos_relacionados,
                'form_resena': form_resena,
                'error': "Error al actualizar el producto"
            })
    
    # Contexto común para GET y POST fallido
    context = {
        'producto': producto,
        'form': form,
        'resenas': resenas,
        'promedio_calificacion': promedio_calificacion,
        'productos_relacionados': productos_relacionados,
        'form_resena': form_resena,
    }
    
    # Determinar qué plantilla usar
    template = 'productos/detalle_producto_mascota.html' if slug else 'producto_detail.html'
    
    return render(request, template, context)


# Vista para listar productos por categoría
def productos_por_categoria(request, slug):
    categoria = get_object_or_404(CategoriaMascota, slug=slug)
    productos = Productos.objects.filter(categoria=categoria)

 # Aplicar filtros
    form = FiltroProductoMascotaForm(request.GET)
    if form.is_valid():
 # Filtrar por tipo de mascota
        if form.cleaned_data.get('tipo_mascota'):
                productos = productos.filter(tipo_mascota=form.cleaned_data['tipo_mascota'])

 # Filtrar por rango de precio
        if form.cleaned_data.get('precio_min'):
            productos = productos.filter(precio__gte=form.cleaned_data['precio_min'])

        if form.cleaned_data.get('precio_max'):
            productos = productos.filter(precio__lte=form.cleaned_data['precio_max'])

 # Buscar por texto
        if form.cleaned_data.get('busqueda'):
            busqueda = form.cleaned_data['busqueda']
            productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(description__icontains=busqueda)
 )

 # Ordenar resultados
        if form.cleaned_data.get('orden'):
            productos = productos.order_by(form.cleaned_data['orden'])

 # Paginación
        paginator = Paginator(productos, 12) # 12 productos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categorias = CategoriaMascota.objects.all()

        context = {
            'categoria': categoria,
            'form': form,
            'page_obj': page_obj,
            'productos': page_obj,
            'categorias': categorias,
}

    return render(request, 'productos/productos_por_categoria.html', context)

        
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
        
