from django.db import models
from ..personas.models import Rol
from django.contrib.auth.models import User

# Este model define el usuario y el Rol que ocupa

class UserRol(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
