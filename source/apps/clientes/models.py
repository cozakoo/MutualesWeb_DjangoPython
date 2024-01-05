from apps.personas.models import Rol


class Cliente(Rol):
    TIPO = 2

    def __str__(self):
        return f"{self.persona.nombre} {self.persona.apellido}"

Rol.register(Cliente)