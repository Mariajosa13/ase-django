from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from tasks.models import Cliente, Domiciliario, Productos, Profile, CategoriaMascota, Tienda
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib import messages
from tasksCliente.forms import SignupForm, ProfileUpdateForm


# Create your views here.
def home(request):
    return render(request, 'home.html')

# Vista para registrar un nuevo usuario
def signup(request):
    if request.method == 'GET':
        signup_form = SignupForm(prefix='signup')
        signin_form = AuthenticationForm(prefix='signin')

        return render(request, 'signup.html', {
            'signup_form': signup_form,
            'signin_form': signin_form,
        })
    else:
        # Se maneja el registro
        if 'register_submit' in request.POST:
            form = SignupForm(request.POST, prefix='signup')
            if form.is_valid():
                print(f"DEBUG: Username para create_user: '{form.cleaned_data['username']}'")
                
                try:
                    # Se crea el usuario. La señal post_save creará el objeto Profile asociado.
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password']
                    )

                    # Recupera el perfil que fue creado automáticamente por la señal
                    profile = user.profile 

                    # Actualiza los campos del perfil con los datos del formulario
                    profile.nombre = form.cleaned_data['nombre']
                    profile.apellido = form.cleaned_data['apellido']
                    profile.correo = form.cleaned_data.get('correo', '')
                    profile.tipo_usuario = form.cleaned_data.get('tipo_usuario', 'cliente')

                    profile.save() # Guarda los cambios en el perfil

                    tipo_usuario = profile.tipo_usuario.strip().lower() 

                    if tipo_usuario == 'cliente':
                        cliente, created = Cliente.objects.get_or_create(profile=profile) # Usar get_or_create para evitar duplicados
                        cliente.segundo_apellido = form.cleaned_data.get('segundo_apellido', '')
                        cliente.celular = form.cleaned_data.get('celular', '')
                        cliente.genero = form.cleaned_data.get('genero', '')
                        
                        fecha_nacimiento_str = form.cleaned_data.get('fecha_nacimiento')
                        if fecha_nacimiento_str:
                            try:
                                cliente.fecha_nacimiento = fecha_nacimiento_str 
                            except ValueError: # Este es menos probable ahora si el form ya validó la fecha
                                print("Formato de fecha de nacimiento incorrecto para cliente.")
                                pass
                        else:
                            cliente.fecha_nacimiento = None
                        cliente.save()
                        
                    elif tipo_usuario == 'domiciliario':
                        domiciliario, created = Domiciliario.objects.get_or_create(profile=profile)
                        domiciliario.vehiculo = form.cleaned_data.get('vehiculo', '')
                        domiciliario.segundo_apellido = form.cleaned_data.get('segundo_apellido', '')
                        domiciliario.celular = form.cleaned_data.get('celular', '')
                        domiciliario.genero = form.cleaned_data.get('genero', '')
                        
                        fecha_nacimiento_str_dom = form.cleaned_data.get('fecha_nacimiento')
                        if fecha_nacimiento_str_dom:
                            try:
                                domiciliario.fecha_nacimiento = fecha_nacimiento_str_dom
                            except ValueError:
                                print("Formato de fecha de nacimiento incorrecto para domiciliario.")
                                pass
                        else:
                            domiciliario.fecha_nacimiento = None
                        domiciliario.save()
                        
                    elif tipo_usuario == 'tienda':
                        tienda, created = Tienda.objects.get_or_create(profile=profile)
                        tienda.nombre_tienda = form.cleaned_data.get('nombre_tienda', '')
                        tienda.nit = form.cleaned_data.get('nit', '')
                        tienda.save()
                    
                    login(request, user) # Inicia sesión al usuario después del registro
                    messages.success(request, '¡Registro exitoso! Te has logueado automáticamente.')
                    
                    # Redirección según el tipo de usuario
                    if tipo_usuario == 'cliente':
                        return redirect('productos')
                    elif tipo_usuario == 'domiciliario':
                        return redirect('dashboard_domiciliario')
                    elif tipo_usuario == 'tienda':
                        return redirect('dashboard_tienda')
                    else:
                        return redirect('home')

                except IntegrityError as e:
                    print(f"IntegrityError during signup: {e}")
                    signup_form = form
                    signin_form = AuthenticationForm(prefix='signin')
                    messages.error(request, '⚠️ El nombre de usuario ya existe o hay un problema de datos.')
                    return render(request, 'signup.html', {
                        'signup_form': signup_form,
                        'signin_form': signin_form,
                        "error": '⚠️ El nombre de usuario ya existe o hay un problema de datos.' # Mensaje de error más específico
                    })
                except Exception as e:
                    print(f"Error inesperado durante signup: {e}")
                    signup_form = form
                    signin_form = AuthenticationForm(prefix='signin')
                    messages.error(request, f'❌ Ocurrió un error inesperado al registrarse: {e}')
                    return render(request, 'signup.html', {
                        'signup_form': signup_form,
                        'signin_form': signin_form,
                        "error": f'❌ Ocurrió un error inesperado al registrarse: {e}'
                    })
            else:
                # El formulario de registro no es válido
                signup_form = form # Muestra el formulario con los errores
                signin_form = AuthenticationForm(prefix='signin')
                messages.error(request, 'Por favor, corrige los errores en el formulario de registro.')
                return render(request, 'signup.html', {
                    'signup_form': signup_form,
                    'signin_form': signin_form,
                    "error": form.errors.as_text() # Muestra los errores del formulario
                })

        # Manejar el inicio de sesión (si el formulario de login fue enviado a esta vista)
        elif 'login_submit' in request.POST:
            form = AuthenticationForm(request.POST, prefix='signin')
            if form.is_valid():
                user = form.get_user()
                login(request, user)

                try:
                    profile = Profile.objects.get(user=user)
                    tipo_usuario = profile.tipo_usuario.strip().lower()

                    print("Tipo de usuario (Signin):", tipo_usuario)

                    if tipo_usuario == 'cliente':
                        return redirect('productos')
                    elif tipo_usuario == 'domiciliario':
                        return redirect('dashboard_domiciliario')
                    elif tipo_usuario == 'tienda':
                        return redirect('dashboard_tienda')
                    else:
                        return redirect('home')

                except Profile.DoesNotExist:
                    # Si el usuario existe pero no tiene un perfil (poco probable con las señales)
                    signup_form = SignupForm(prefix='signup')
                    signin_form = form
                    messages.error(request, 'Este usuario no tiene perfil asignado.')
                    return render(request, 'signup.html', {
                        'signup_form': signup_form,
                        'signin_form': signin_form,
                        'error': 'Este usuario no tiene perfil asignado'
                    })
            else:
                # El formulario de inicio de sesión no es válido
                signup_form = SignupForm(prefix='signup')
                signin_form = form
                messages.error(request, 'Usuario o contraseña son incorrectos.')
                return render(request, 'signup.html', {
                    'signup_form': signup_form,
                    'signin_form': signin_form,
                    'error': 'Usuario o contraseña son incorrectos.'
                })
        else:
            signup_form = SignupForm(prefix='signup')
            signin_form = AuthenticationForm(prefix='signin')
            messages.error(request, 'Solicitud desconocida.')
            return render(request, 'signup.html', {
                'signup_form': signup_form,
                'signin_form': signin_form,
                'error': 'Solicitud desconocida.'
            })

# para cerrar sesión
@login_required
def signout(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        signup_form = SignupForm(prefix='signup')
        signin_form = AuthenticationForm(prefix='signin')
        return render(request, 'signup.html', {
            'signup_form': signup_form,
            'signin_form': signin_form,
        })
    else:
        form = AuthenticationForm(data=request.POST, prefix='signin')
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            try:
                profile = Profile.objects.get(user=user)
                tipo_usuario = profile.tipo_usuario.strip().lower()

                print("Tipo de usuario: (Signin) ", tipo_usuario)

                if tipo_usuario == 'cliente':
                    return redirect('productos')
                elif tipo_usuario == 'domiciliario':
                    return redirect('dashboard_domiciliario')
                elif tipo_usuario == 'tienda':
                    return redirect('dashboard_tienda')
                else:
                    return redirect('home')

            except Profile.DoesNotExist:
                signup_form = SignupForm(prefix='signup')
                signin_form = form
                messages.error(request, 'Este usuario no tiene perfil asignado.')
                return render(request, 'signup.html', {
                    'signup_form': signup_form,
                    'signin_form': signin_form,
                    'error': 'Este usuario no tiene perfil asignado'
                })
        else:
            signup_form = SignupForm(prefix='signup')
            signin_form = form
            messages.error(request, 'Usuario o contraseña son incorrectos.')
            return render(request, 'signup.html', {
                'signup_form': signup_form,
                'signin_form': signin_form,
                'error': 'Usuario o contraseña son incorrectos'
            })


#######################################
@login_required
def perfil_detalle(request):
    # Muestra la información del perfil del usuario que se creo al registrarse
    profile = get_object_or_404(Profile, user=request.user)
    
    # Intenta obtener los perfiles específicos si existen
    cliente_profile = None
    domiciliario_profile = None
    tienda_profile = None

    if profile.tipo_usuario == 'cliente':
        cliente_profile = Cliente.objects.filter(profile=profile).first()
    elif profile.tipo_usuario == 'domiciliario':
        domiciliario_profile = Domiciliario.objects.filter(profile=profile).first()
    elif profile.tipo_usuario == 'tienda':
        tienda_profile = Tienda.objects.filter(profile=profile).first()

    return render(request, 'perfil_detalle.html', {
        'profile': profile,
        'cliente_profile': cliente_profile,
        'domiciliario_profile': domiciliario_profile,
        'tienda_profile': tienda_profile,
    })

@login_required
def perfil_editar(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    # Se toma el formulario de actualización de perfil y se actualiza información como se define en este
    if request.method == 'POST':
        # Instancia el form con los datos POST y la instancia del perfil
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
    # Estos campos son parte de Cliente/Domiciliario, no directamente de Profile.
    
    campos_permitidos_cliente = ['segundo_apellido', 'celular', 'genero', 'fecha_nacimiento']
    campos_permitidos_domiciliario = ['segundo_apellido', 'celular', 'genero', 'fecha_nacimiento', 'vehiculo']

    profile = get_object_or_404(Profile, user=request.user)
    
    if profile.tipo_usuario == 'cliente':
        related_profile_obj = Cliente.objects.filter(profile=profile).first()
        if not related_profile_obj or campo not in campos_permitidos_cliente:
            messages.error(request, 'No se puede eliminar este campo o no pertenece a tu tipo de usuario.')
            return redirect('perfil_editar')
        
    elif profile.tipo_usuario == 'domiciliario':
        related_profile_obj = Domiciliario.objects.filter(profile=profile).first()
        if not related_profile_obj or campo not in campos_permitidos_domiciliario:
            messages.error(request, 'No se puede eliminar este campo o no pertenece a tu tipo de usuario.')
            return redirect('perfil_editar')
            
    else:
        messages.error(request, 'Tu tipo de usuario no permite eliminar campos de esta forma.')
        return redirect('perfil_editar')

    # Si existe lo pone en none (campo vacío)
    if hasattr(related_profile_obj, campo):
        setattr(related_profile_obj, campo, None)
        related_profile_obj.save()
        messages.success(request, f'El campo {campo} ha sido eliminado.')
    else:
        messages.error(request, 'Campo no encontrado en tu perfil específico.')
        
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



# Vista domi al iniciar sesión

def dashboard_domiciliario(request):
    return render(request, 'dashboard_domiciliario.html')