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
from django.contrib import messages
from .forms import ResenaProductoMascotaForm, FiltroProductoMascotaForm, ProductoForm, SignupForm, ProfileUpdateForm


# Create your views here.
def home(request):
    return render(request, 'home.html')

# Vista para registrar un nuevo usuario
def signup(request):
    # Muestra el formulario con GET
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': SignupForm()
        })
    else:
        # Se envia la información y valida que las contraseñas coincidan
        if request.POST['password1'] == request.POST['password2']:
            try:

                # Crea un usuario y un perfil y se guarda
                user = User.objects.create_user(username=request.POST['usuario'], password=request.POST['password1'])
                user.save()

                profile = Profile(
                    user=user,
                    nombre=request.POST['nombre'],
                    apellido=request.POST['apellido'],
                    correo=request.POST['correo']
                )
                profile.save()

                # Inicia sesión y  lo redirige a los productos
                login(request, user)
                return redirect('productos')
            
            # Si trata de registrarse con un usuario existente IntegrityError no lo permite
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': SignupForm(),
                    "error": '⚠️ El nombre de usuario ya existe.'
                })
            
        # Se recibe información desde el html y si el usuario ingresa contraseñas diferentes manda el error
        return render(request, 'signup.html', {
            'form': SignupForm(),
            "error": '❌ Las contraseñas no coinciden.'
        })

#para cerrar sesión
@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    # Muestra el formulario con GET
    if request.method == 'GET':
        return render(request, 'signin.html', {
        'form': AuthenticationForm
    })
    else:
        #Si es POST verifica si el usuario existe con ese usuario y contraseña
        user = authenticate(request, username=request.POST['usuario'], password=request.POST['password1'])
        
        # Si el usuario no existe manda error
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña son incorrectos'
                })
        else:
            #Si el usuario existe lo redirige a la página de productos
            login(request, user)
            return redirect('productos')


@login_required
def perfil_detalle(request):
    #Muestra la información del perfil del usuario que se creo al registrarse
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'perfil_detalle.html', {'profile': profile})

@login_required
def perfil_editar(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    # Se toma el formulario de actualización de perfil y se actualiza información como se define en este
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('perfil_detalle')
    else:
        form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'perfil_editar.html', {'form': form})

@login_required
def eliminar_campo(request, campo):
    # Se eliminan campos permitidos
    campos_permitidos = ['segundo_apellido', 'celular', 'genero']
    
    if campo not in campos_permitidos:
        messages.error(request, 'No se puede eliminar este campo.')
        return redirect('perfil_editar')
    
    #Busca el perfil del ususario
    profile = get_object_or_404(Profile, user=request.user)
    
    # hasattr verifica si en el perfil si existe el campo que se va a eliminar
    if hasattr(profile, campo):
    # Si existe lo pone en none (campo vacío)
        setattr(profile, campo, None)
        profile.save()
        messages.success(request, f'El campo {campo} ha sido eliminado.')
    else:
        messages.error(request, 'Campo no encontrado.')
        
    return redirect('perfil_detalle')

def productos(request):
    #Muestra todos los productos
    productos = Productos.objects.all()
    return render(request, 'productos.html', {'productos': productos})

def producto_list(request):
    #Toma el formulario de Filtros de productos
    form = FiltroProductoMascotaForm(request.GET)
    productos = Productos.objects.all()

    if form.is_valid():
 # Lo filtra por categoría
        if form.cleaned_data.get('categoria'):
            productos = productos.filter(categoria=form.cleaned_data['categoria'])

 # Lo filtra por tipo de mascota
        if form.cleaned_data.get('tipo_mascota'):
            productos = productos.filter(tipo_mascota=form.cleaned_data['tipo_mascota'])

 # Lo filtra por rango de precio max o min
        if form.cleaned_data.get('precio_min'):
            productos = productos.filter(precio__gte=form.cleaned_data['precio_min'])

        if form.cleaned_data.get('precio_max'):
            productos = productos.filter(precio__lte=form.cleaned_data['precio_max'])

 # Lo busca por texto
        if form.cleaned_data.get('busqueda'):
            busqueda = form.cleaned_data['busqueda']
            productos = productos.filter(
                Q(nombre__icontains=busqueda) |
                Q(description__icontains=busqueda)
 )

 # Ordena todos los resultados
        if form.cleaned_data.get('orden'):
            productos = productos.order_by(form.cleaned_data['orden'])

 # Permite 12 productos por página con el Paginator de django
        paginator = Paginator(productos, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        categorias = CategoriaMascota.objects.all()

        context = {
            'form': form,
            'page_obj': page_obj,
            'productos': page_obj,
            'categorias': categorias,
}
    return render(request, 'productos/producto_list.html', context)

@login_required
def producto_detail(request, producto_id=None, slug=None):
    # Esta vista muestra el detalle de un producto específico.
    # El producto se puede buscar usando su 'producto_id' o su 'slug' (texto mas bonito en URLs).

    # se obtiene el producto usando el 'producto_id' si está disponible
    if producto_id:
        producto = get_object_or_404(Productos, pk=producto_id)
    # Si no hay 'producto_id', se busca usando el 'slug'
    elif slug:
        producto = get_object_or_404(Productos, slug=slug)
    # Si no se proporcionó ni 'producto_id' ni 'slug', devolvemos un error 400 (Bad Request)
    else:
        return HttpResponseBadRequest("No se proporcionó un identificador de producto")
    
    # se obtienen todas las reseñas asociadas al producto (si existen) desde la más reciente a la más antigua.
    resenas = producto.resenas.all().order_by('-fecha_creacion') if hasattr(producto, 'resenas') else None
    promedio_calificacion = producto.resenas.aggregate(Avg('calificacion'))['calificacion__avg'] if hasattr(producto, 'resenas') else None
    productos_relacionados = None

    # Si el producto tiene una categoría asignada (y no está vacía) se buscan productos relacionaos,
    if hasattr(producto, 'categoria') and producto.categoria:
        productos_relacionados = Productos.objects.filter(
            categoria=producto.categoria
        ).exclude(id=producto.id)[:4]

    return render(request, 'producto_detail.html', {
        'producto': producto,
        'resenas': resenas,
        'promedio_calificacion': promedio_calificacion,
        'productos_relacionados': productos_relacionados,
    })


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
        paginator = Paginator(productos, 12)
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
#Debe editarse y que sea para administradores
def delete_producto(request, producto_id):
    producto = get_object_or_404(Productos, pk=producto_id, user=request.user)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos')

@login_required
#se debe editar
def agregar_resena(request, slug):
    producto = get_object_or_404(Productos, slug=slug)

    #guarda reseña asociada al usuario y el producto
    if request.method == 'POST':
        form = ResenaProductoMascotaForm(request.POST)
        if form.is_valid():
            reseña = form.save(commit=False)
            reseña.producto = producto
            reseña.usuario = request.user
            reseña.save()
            return redirect('producto_detail', slug=producto.slug)
    else:
        form = ResenaProductoMascotaForm()

    return render(request, 'agregar_resena.html', {
        'form': form,
        'producto': producto
    })


        
