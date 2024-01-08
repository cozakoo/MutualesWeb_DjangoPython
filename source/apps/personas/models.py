import re
from django.db import models
from utils.regularexpressions import alpha_validator, telefono_validator
from django.core.exceptions import ValidationError


class Persona(models.Model):
    nombre = models.CharField(max_length=50, validators=[alpha_validator])
    apellido = models.CharField(max_length=50, validators=[alpha_validator])
    clave = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15, validators=[telefono_validator])
    correo = models.EmailField()
    es_empleado_publico = models.BooleanField(default=False)
    es_cliente = models.BooleanField(default=False)
    
    def clean(self):
        super().clean()
        
        # Validar campos alfabéticos
        for field in ['nombre', 'apellido']:
            value = getattr(self, field)
            if not re.match(alpha_validator.regex, value):
                raise ValidationError(f'{field.capitalize()} no cumple con el formato permitido.')

class Rol(models.Model):
    TIPO = 0
    TIPOS = []
    persona = models.ForeignKey(Persona, related_name="roles", on_delete=models.CASCADE)
    tipo = models.PositiveSmallIntegerField(choices=TIPOS)
    
    @classmethod
    def register(cls, Klass):
        cls.TIPOS.append((Klass.TIPO, Klass.__name__.lower()))