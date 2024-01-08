# Importaciones del sistema
from django.urls import path
from .views import *

app_name = "clientes"

urlpatterns = [
    path('crear/',ClienteCreateView.as_view(), name="cliente_crear"),
    path('confirmacion/', confirmacion_cliente, name='confirmacion_cliente'),

]