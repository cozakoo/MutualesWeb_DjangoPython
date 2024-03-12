"""
Funciones diseñadas para simplificar y mejorar la presentación de mensajes.

"""

from django.contrib import messages

# -------------- ICONOS ------------------------------------------
ICON_ERROR = '<i class="fa-solid fa-x fa-beat-fade"></i>'
ICON_CHECK = '<i class="fa-solid fa-square-check fa-beat-fade"></i>'
ICON_TRIANGLE = '<i class="fa-solid fa-triangle-exclamation fa-flip"></i>'

# ------------- FUNCIONES PARA MENSAJES ------------------
def mensaje_error(request, message):
    messages.error(request, f'{ICON_ERROR} {message}')

def mensaje_exito(request, message):
    messages.success(request, f'{ICON_CHECK} {message}')

def mensaje_advertencia(request, message):
    messages.warning(request, f'{ICON_TRIANGLE} {message}')