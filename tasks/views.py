from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.core.paginator import Paginator
from .models import Productos, Profile, CategoriaMascota, ResenaProductoMascota
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib import messages
from tasksCliente.forms import ResenaProductoMascotaForm, SignupForm, ProfileUpdateForm


#######################################
        
# @login_required
# #Debe editarse y que sea para administradores
# def delete_producto(request, producto_id):
#     producto = get_object_or_404(Productos, pk=producto_id, user=request.user)
#     if request.method == 'POST':
#         producto.delete()
#         return redirect('productos')

# @login_required
# #se debe editar
# def agregar_resena(request, slug):
#     producto = get_object_or_404(Productos, slug=slug)

#     #guarda reseña asociada al usuario y el producto
#     if request.method == 'POST':
#         form = ResenaProductoMascotaForm(request.POST)
#         if form.is_valid():
#             reseña = form.save(commit=False)
#             reseña.producto = producto
#             reseña.usuario = request.user
#             reseña.save()
#             return redirect('producto_detail', slug=producto.slug)
#     else:
#         form = ResenaProductoMascotaForm()

#     return render(request, 'agregar_resena.html', {
#         'form': form,
#         'producto': producto
#     })


        
