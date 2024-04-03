# middleware.py
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.conf import settings
from apps.users.models import UserRol
from django.contrib.auth import logout


def ActualizarUltimaActividad(user):
    userRol = UserRol.objects.get(user = user)
    userRol.ultimaActividad = timezone.now()
    userRol.save()


def obtenerUltimaActividad(user):
    try:
        u = UserRol.objects.get(user = user)
        print("devolvi info")
        return u.ultimaActividad
      
    except UserRol.DoesNotExist:
        return None
    
class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("midelware")
        response = self.get_response(request)

        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            # Obtener la última actividad de la sesión
            last_activity = obtenerUltimaActividad(request.user)
            print(last_activity)
            print("IF")
            if last_activity:
                # Calcular el tiempo transcurrido desde la última actividad
                idle_time = timezone.now() - last_activity
                print("PASE")
                print(idle_time.total_seconds)
                if idle_time.total_seconds() > settings.SESSION_COOKIE_AGE:
                    # Si el tiempo de inactividad supera la duración de la sesión, cerrar la sesión
                    logout(request)

            # Actualizar la última actividad en la sesión
            ActualizarUltimaActividad(request.user)

        return response