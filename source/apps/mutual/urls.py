# Importaciones del sistema
from django.urls import path
from .views import mutual_exito, MutualCreateView, DeclaracionJuradaView, tu_vista, DetalleMutualView


app_name = "mutual"

urlpatterns = [
    path('crearMutual/',MutualCreateView.as_view(), name="mutual_crear"),
    path('nuevaDeclaracionJurada/',DeclaracionJuradaView.as_view(), name="declaracion_jurada"),

    # path('declararReclamo/',DeclaracionJuradaReclamo.as_view(), name="declarar_reclamo"),
    # path('crearDj/',DeclaracionJuradaCreateView.as_view(), name="dj_crear"),
    path('exito/', mutual_exito, name='mutual_exito'),
    path('prueba/', tu_vista, name='t_vista'),
    path('miMutual/', DetalleMutualView.as_view(), name='detalles_mimutual'),
    # path('dj_confirmacion/', , name='t_vista'),
    
]