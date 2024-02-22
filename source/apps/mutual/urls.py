# Importaciones del sistema
from django.urls import path
from .views import HistoricoView, descargarDeclaracion, mutual_exito, MutualCreateView, DeclaracionJuradaView, tu_vista, DetalleMutualView ,ConfirmacionView, MsjInformativo,VisualizarErroresView
app_name = "mutual"

urlpatterns = [
    path('crearMutual/',MutualCreateView.as_view(), name="mutual_crear"),
    path('nuevaDeclaracionJurada/',DeclaracionJuradaView.as_view(), name="declaracion_jurada"),
    # path('nuevaDeclaracionJurada/',DeclaracionJuradaView.as_view(), name="historico"),
    path('DeclaracionJurada/Historico',HistoricoView.as_view(), name="historico"),
    path('DeclaracionJurada/<int:pk>/', descargarDeclaracion, name="descargarDeclaracion"),

    # path('declararReclamo/',DeclaracionJuradaReclamo.as_view(), name="declarar_reclamo"),
    # path('crearDj/',DeclaracionJuradaCreateView.as_view(), name="dj_crear"),
    path('exito/', mutual_exito, name='mutual_exito'),
    path('prueba/', tu_vista, name='t_vista'),
    path('miMutual/', DetalleMutualView.as_view(), name='detalles_mimutual'),
    path('confirmacion/', ConfirmacionView.as_view(), name='confirmacion'),
    path('visualizar_errores/', VisualizarErroresView.as_view(), name='visualizarE'),
    path('msj_informativo/', MsjInformativo.as_view(), name='msj_info'),
    
    # path('dj_confirmacion/', , name='t_vista'),
    
]