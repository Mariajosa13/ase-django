from django.contrib import admin
from .models import Productos, Profile, Cart, CartItem, CategoriaMascota, Cliente, Domiciliario, Tienda, Direccion, ApiKey

# --- Productos Admin ---
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'tipo_mascota', 'user', 'created', 'destacado')
    list_display_links = ('nombre',) 
    readonly_fields = ("created",)
    search_fields = ('nombre', 'description', 'tipo_mascota') 
    list_filter = ('tipo_mascota', 'categoria', 'destacado') 
    date_hierarchy = 'created'

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('profile', 'nombre_quien_recibe', 'pais', 'departamento', 'ciudad', 'direccion', 'codigo_postal', 'telefono', 'es_predeterminada')
    list_display_links = ('profile', 'nombre_quien_recibe', 'direccion',)
    search_fields = ('profile__user__username', 'nombre_quien_recibe', 'direccion', 'ciudad', 'telefono')
    list_filter = ('pais', 'departamento', 'ciudad', 'es_predeterminada')

class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 1

# --- Profile Admin ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'nombre', 'apellido', 'correo', 'fecha_nacimiento')
    list_display_links = ('user',)
    search_fields = ('user__username', 'nombre', 'apellido', 'correo')
    list_filter = ('tipo_usuario',)
    inlines = [DireccionInline] 


# --- Cart Admin ---
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'created_at', 'updated_at', 'get_total_price_display')
    list_display_links = ('user',)
    readonly_fields = ('created_at', 'updated_at')

    def get_total_price_display(self, obj):
        return f"${obj.get_total_price():,.2f}"
    get_total_price_display.short_description = "Total Price"




# --- CartItem Admin ---
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'producto', 'quantity', 'added_at', 'get_total_item_price')
    list_display_links = ('producto',)
    readonly_fields = ('added_at',)
    list_filter = ('cart__user',) 

    def get_total_item_price(self, obj):
        return f"${obj.get_total_price():,.2f}"
    get_total_item_price.short_description = "Item Total"

# --- CategoriaMascota Admin ---
@admin.register(CategoriaMascota)
class CategoriaMascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    list_display_links = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

# --- Cliente Admin ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'celular', 'genero')
    list_display_links = ('profile',)
    search_fields = ('profile__user__username', 'celular')


# --- Domiciliario Admin ---
@admin.register(Domiciliario)
class DomiciliarioAdmin(admin.ModelAdmin):
    list_display = ('profile', 'vehiculo', 'celular', 'genero')
    list_display_links = ('profile',)
    search_fields = ('profile__user__username', 'vehiculo', 'celular')

# --- Tienda Admin ---
@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('tienda', 'key', 'created_at')
    readonly_fields = ('key', 'created_at')
    search_fields = ('tienda__nombre_tienda', 'tienda__profile__user__username')
    # evitar creación manual desde admin (opcional)
    def has_add_permission(self, request):
        return False

@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('profile', 'nombre_tienda', 'nit')
    search_fields = ('nombre_tienda','profile__user__username')