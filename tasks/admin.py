from django.contrib import admin
from .models import Productos, Profile, Cart, CartItem, CategoriaMascota, Cliente, Domiciliario, Tienda

# --- Productos Admin ---
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    # 'id' is automatically displayed, no need to include it unless you want it explicitly first
    list_display = ('nombre', 'precio', 'stock', 'tipo_mascota', 'user', 'created', 'destacado')
    list_display_links = ('nombre',) # Only 'nombre' is usually enough as a link
    readonly_fields = ("created",) # Make 'created' field read-only in the admin form
    search_fields = ('nombre', 'description', 'tipo_mascota') # Add search capability
    list_filter = ('tipo_mascota', 'categoria', 'destacado') # Add filters for easier navigation
    date_hierarchy = 'created' # Add a date drill-down navigation for 'created' field

# --- Profile Admin ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'nombre', 'apellido', 'correo', 'fecha_nacimiento')
    list_display_links = ('user',)
    search_fields = ('user__username', 'nombre', 'apellido', 'correo') # Search by related User's username too
    list_filter = ('tipo_usuario',)

# --- Cart Admin ---
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'created_at', 'updated_at', 'get_total_price_display')
    list_display_links = ('user',)
    readonly_fields = ('created_at', 'updated_at')

    # Custom method to display total price in list_display
    def get_total_price_display(self, obj):
        return f"${obj.get_total_price():,.2f}"
    get_total_price_display.short_description = "Total Price"


# --- CartItem Admin ---
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'producto', 'quantity', 'added_at', 'get_total_item_price')
    list_display_links = ('producto',)
    readonly_fields = ('added_at',)
    list_filter = ('cart__user',) # Filter by the user associated with the cart

    # Custom method to display total price for the item
    def get_total_item_price(self, obj):
        return f"${obj.get_total_price():,.2f}"
    get_total_item_price.short_description = "Item Total"

# --- CategoriaMascota Admin ---
@admin.register(CategoriaMascota)
class CategoriaMascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    list_display_links = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)} # Automatically generate slug from name

# --- Cliente Admin ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'celular', 'genero')
    list_display_links = ('profile',)
    search_fields = ('profile__user__username', 'celular') # Search by related Profile's user username

# --- Domiciliario Admin ---
@admin.register(Domiciliario)
class DomiciliarioAdmin(admin.ModelAdmin):
    list_display = ('profile', 'vehiculo', 'celular', 'genero')
    list_display_links = ('profile',)
    search_fields = ('profile__user__username', 'vehiculo', 'celular')

# --- Tienda Admin ---
@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('profile', 'nombre_tienda', 'nit')
    list_display_links = ('profile', 'nombre_tienda')
    search_fields = ('profile__user__username', 'nombre_tienda', 'nit')
