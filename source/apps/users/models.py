from django.db import models
from ..personas.models import Rol
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
# Este model define el usuario y el Rol que ocupa

class UserRol(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    ultimaConexion = models.DateTimeField(null=True, blank=True)  # Nuevo campo para almacenar la última conexión

    def __str__(self):
        return f"{self.user.username} "