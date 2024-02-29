from django.db import models
from ..personas.models import Rol

# Create your models here.
class EmpleadoPublico(Rol):
    TIPO = 3


Rol.register(EmpleadoPublico)