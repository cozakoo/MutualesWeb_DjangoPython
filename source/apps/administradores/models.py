from django.db import models
from apps.personas.models import Rol
from utils.regularexpressions import alpha_validator

# Create your models here.
class Administrador(Rol):
    TIPO = 2
    nombre = models.CharField(max_length=50, validators=[alpha_validator])
    apellido = models.CharField(max_length=50, validators=[alpha_validator])
    def __str__(self):
        return f"{self.persona.nombre} {self.persona.apellido}"

Rol.register(Administrador)