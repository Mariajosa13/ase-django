from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from tasks.models import ApiKey, Profile
from django.contrib.auth.models import AnonymousUser

class ApiKeyAuthBackend(BaseAuthentication):
    """
    Clase de Autenticación de DRF para validar la API Key.
    Devuelve (user, auth) si es exitoso.
    """
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')
        
        if not api_key:
            return None #retorna None si no hay clave, permite otros métodos de auth.
        
        api_key_clean = api_key.strip()

        try:
            # busca con la relación corregida (Tienda -> Profile -> User)
            api_key_obj = ApiKey.objects.select_related('tienda', 'tienda__profile', 'tienda__profile__user').get(key=api_key_clean)
            
            profile = api_key_obj.tienda.profile 
            
            if profile.tipo_usuario.strip().lower() != 'tienda':
                 #si la clave es válida pero el usuario no es tienda, denegar.
                 raise exceptions.AuthenticationFailed('La API Key no pertenece a una tienda autorizada.')

            user = profile.user
            #adjuntar profile al request (DRF no lo hace automáticamente)
            request.profile = profile 
            
            #usa la clave limpia como token.
            return (user, api_key_clean) 

        except ApiKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('API Key inválida o inexistente.')
        except Exception:
            raise exceptions.AuthenticationFailed('Error de autenticación.')

        return None