
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db import IntegrityError
from tasks.models import Profile, Productos, ApiKey, Tienda
from .forms import SignupFormTienda, ProductoForm

def dashboard_tienda(request):
    return render(request, 'dashboard_tienda.html')

# Vista para registrar un nuevo usuario
def signupTienda(request):
    if request.method == 'GET':
        form = SignupFormTienda()
        return render(request, 'signupTienda.html', {
            'signupTienda_form': form,
        })
    else:
        form = SignupFormTienda(request.POST)
        # Se maneja el registro
        if form.is_valid():
            try:
                user, api_key_str = form.save()

                login(request, user)  # Inicia sesión al usuario después del registro
                messages.success(request, f'¡Registro exitoso! Tu **API Key** es: {api_key_str}. Guárdala en un lugar seguro. ¡Es muy importante! ')
                return redirect('tienda:dashboard_tienda')
            
            except IntegrityError:
                messages.error(request, 'El nombre de usuario o correo ya están en uso.')
            except Exception as e:
                messages.error(request, f'Error durante el registro: {e}')

        return render(request, 'signupTienda.html', {'signupTienda_form': form, "error": form.errors.as_text()})

def signinTienda(request):
    if request.method == 'GET':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            try:
                profile = Profile.objects.get(user=user)
                tipo_usuario = profile.tipo_usuario.strip().lower()

                if tipo_usuario == 'tienda':
                    return redirect('tienda:dashboard_tienda')
                else:
                    messages.error(request, 'Acceso denegado. No eres un usuario de tipo Tienda.')
                    logout(request)
                    return redirect('signinTienda')
            except Profile.DoesNotExist:
                messages.error(request, 'Este usuario no tiene perfil asignado.')
        messages.error(request, 'Usuario o API Key/contraseña incorrectos.')

        signin_form = AuthenticationForm()
        return render(request, 'signin.html', {'signin_form': signin_form})
    
# para cerrar sesión
@login_required
def signoutTienda(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('tienda:signupTienda')

@login_required
def dashboard_tienda(request):
    user = request.user
    
    try:
        profile = user.profile
        if profile.tipo_usuario != 'tienda':
            messages.error(request, "Acceso denegado.")
            return redirect('tienda:signupTienda')
    except Profile.DoesNotExist:
        messages.error(request, "Perfil no encontrado.")
        return redirect('tienda:signoutTienda') 
        
    # obtener la Tienda
    tienda_info = getattr(profile, 'tienda', None)
    if tienda_info is None:
        messages.error(request, "No se encontró la tienda asociada a este usuario.")
        return redirect('tienda:signupTienda')
    
     # obtener la API Key
    try:
        api_key_str = tienda_info.api_key.key
    except ApiKey.DoesNotExist:
        api_key_str = "No generada. Regenerar ahora."

    # 3. Estadísticas de Productos
    productos_count = Productos.objects.filter(tienda=profile).count()
    productos_en_stock = Productos.objects.filter(tienda=profile, stock__gt=0).count()
    
    context = {
        'profile': profile,
        'tienda_info': tienda_info,
        'api_key': api_key_str,
        'productos_count': productos_count,
        'productos_en_stock': productos_en_stock,
    }
    
    return render(request, 'dashboard_tienda.html', context)

@login_required(login_url='tienda:signinTienda')
def productos_por_tienda(request):
    # verificar si el usuario es una Tienda
    profile = request.user.profile
    if profile.tipo_usuario.strip().lower() != 'tienda':
        messages.error(request, 'Acceso denegado. Solo las tiendas pueden ver esta página.')
        return redirect('tienda:signinTienda') 
    
    # filtrar productos por el Profile de la tienda autenticada
    productos_tienda = Productos.objects.filter(tienda=profile).order_by('-created')
    
    context = {
        'productos': productos_tienda,
        'tienda_nombre': profile.user.username,
    }
    
    # Renderizamos la nueva plantilla
    return render(request, 'productos_tienda_list.html', context)

@login_required(login_url='tienda:signinTienda')
def editar_producto(request, producto_id):
    profile = request.user.profile
    
    producto = get_object_or_404(Productos, id=producto_id)
    
    # solo el dueño puede editar
    if producto.tienda != profile:
        messages.error(request, 'No tienes permiso para editar este producto.')
        return redirect('cliente:productos')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado exitosamente.')
            return redirect('tienda:productos_tienda_list')
    else:
        # GET: Mostrar el formulario con los datos existentes
        form = ProductoForm(instance=producto)

    return render(request, 'editar_producto.html', {
        'form': form,
        'producto': producto,
        'title': f'Editar Producto: {producto.nombre}',
        'is_new': False
    })

@login_required(login_url='tienda:signinTienda')
def eliminar_producto(request, producto_id):
    profile = request.user.profile
    
    producto = get_object_or_404(Productos, id=producto_id)

    # solo el dueño puede eliminar
    if producto.tienda != profile:
        messages.error(request, 'No tienes permiso para eliminar este producto.')
        return redirect('tienda:productos_tienda_list')

    if request.method == 'POST':
        producto.delete()
        messages.success(request, f'Producto "{producto.nombre}" eliminado exitosamente.')
        return redirect('tienda:productos_tienda_list')
    
    # mostrar la página de confirmación de eliminación
    return render(request, 'eliminar_producto.html', {
        'producto': producto
    })

# RECIBIR PRODUCTO EJEMPLO JSON{
#   "nombre": "Cuido de Perro",
#   "description": "Nutra Nuggets",
#   "precio": 120000,
#   "stock": 20,
#   "categoria": null, 
#   "tipo_mascota": "perro"
# }