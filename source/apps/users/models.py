from django.db import models
from ..personas.models import Rol
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.dispatch import receiver
# Este model define el usuario y el Rol que ocupa


class UserRol(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    ultimaConexion = models.DateTimeField(null=True, blank=True)  # Nuevo campo para almacenar la última conexión
    ultimaActividad = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} "


@receiver(user_logged_in, sender=User)
def user_logged_in_callback(sender, request, user, **kwargs):
    print("actualice estado")
    try:
        u = UserRol.objects.get(user = user)
        u.ultimaActividad = timezone.now()
        u.save()
    except UserRol.DoesNotExist:
       print("no tengo userrol")
    