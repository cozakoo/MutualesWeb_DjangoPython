# Importaciones del sistema
from django.urls import path
from .views import mutual_exito, MutualCreateView, DeclaracionJuradaCreateView,tu_vista


app_name = "mutual"

urlpatterns = [
    path('crear/',MutualCreateView.as_view(), name="mutual_crear"),
    path('crearDj/',DeclaracionJuradaCreateView.as_view(), name="dj_crear"),
    path('exito/', mutual_exito, name='mutual_exito'),
    path('prueba/', tu_vista, name='t_vista'),
]