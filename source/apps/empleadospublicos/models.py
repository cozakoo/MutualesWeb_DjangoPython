from django.db import models
from ..personas.models import Rol

# Create your models here.
class EmpleadoPublico(Rol):
    TIPO = 3

    def __str__(self):
        return f"{self.id} {self.mutual.cuit}"

Rol.register(EmpleadoPublico)