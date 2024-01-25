# middleware.py
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.conf import settings

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Actualiza la última actividad del usuario al acceder a cualquier vista
        if request.user.is_authenticated:
            request.user.last_activity = timezone.now()
            request.user.save()

        # Verifica la inactividad y cierra la sesión si es necesario
        self.check_session_timeout(request)

        return response

    def check_session_timeout(self, request):
        # Verifica si el usuario está autenticado y tiene una sesión
        if request.user.is_authenticated and request.session.session_key:
            session = Session.objects.get(session_key=request.session.session_key)

            # Calcula el tiempo de inactividad
            inactive_time = timezone.now() - session.last_activity

            # Cierra la sesión si ha pasado demasiado tiempo de inactividad
            if inactive_time.total_seconds() > settings.SESSION_COOKIE_AGE:
                request.session.flush()

