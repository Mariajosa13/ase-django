# domiciliarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DomiciliarioProfileYDocumentos
from tasks.models import Domiciliario 

@login_required
def completar_perfil(request):
    
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'domiciliario':
        messages.error(request, "No tienes permiso para acceder a esta sección o tu rol no es de domiciliario.")
        return redirect('domiciliario:completar_perfil')

    try:
        domiciliario_profile = Domiciliario.objects.get(profile=request.user.profile)
    except Domiciliario.DoesNotExist:
        # Si el objeto no existe, lo creamos.
        domiciliario_profile = Domiciliario.objects.create(profile=request.user.profile)
    
    if request.method == 'POST':
        form = DomiciliarioProfileYDocumentos(request.POST, request.FILES, instance=domiciliario_profile)
        if form.is_valid():
            form.save()
            # se actualiza el estado de verificación del domiciliario
            if domiciliario_profile.estado_verificacion == 'PENDIENTE_DOCUMENTOS':
                domiciliario_profile.estado_verificacion = 'EN_REVISION'
            domiciliario_profile.save()
            messages.success(request, "Tu información de domiciliario y documentos han sido guardados y están en revisión.")
            return redirect('domiciliario:dashboard')
        else:
            messages.error(request, "Hubo errores al cargar tu información. Por favor, verifica los campos.")
    else:
        form = DomiciliarioProfileYDocumentos(instance=domiciliario_profile)
    
    context = {
        'form': form,
        'domiciliario_profile': domiciliario_profile,
    }
    return render(request, 'completar_perfil.html', context)


@login_required
def domiciliario_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.tipo_usuario != 'domiciliario':
        messages.error(request, "Acceso denegado. No eres un domiciliario.")
        return redirect('dashboard')
    
    domiciliario_profile = get_object_or_404(Domiciliario, profile=request.user.profile)
    
    context = {
        'domiciliario_profile': domiciliario_profile,
    }
    return render(request, 'dashboard.html', context)

