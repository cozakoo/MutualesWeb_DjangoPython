from apps.personas.models import Rol
from django.db import models
from ..mutual.models import Mutual


class Cliente(Rol):
    TIPO = 2
    mutual = models.ForeignKey(Mutual, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.persona.username} {self.mutual.cuit}"

Rol.register(Cliente)