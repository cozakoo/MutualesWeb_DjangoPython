from django.core.validators import RegexValidator

# Definir una expresión regular genérica para validar campos alfabéticos
alpha_regex = r'^[A-Za-z\s]+$'
# Crear un validador de expresión regular genérica
alpha_validator = RegexValidator(
    regex=alpha_regex,
    message='Debe contener solo caracteres alfabéticos y espacios.',
    code='invalid_alpha'
)
#----------------------------------------------------------------------

# Definir una expresión regular para validar números de teléfono
telefono_regex = r'^\+?1?\d{9,15}$'
# Crear un validador de expresión regular para números de teléfono
telefono_validator = RegexValidator(
    regex=telefono_regex,
    message='Ingrese un número de teléfono válido.',
    code='invalid_telefono'
)