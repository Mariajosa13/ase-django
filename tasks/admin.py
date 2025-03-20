from django.contrib import admin
from .models import Productos

@admin.register(Productos)
class RegistrarAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'description', 'precio')
    list_display_links = ('nombre', 'description', 'precio')
    
class ProductosAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )
