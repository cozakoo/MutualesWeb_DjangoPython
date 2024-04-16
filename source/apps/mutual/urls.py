# Importaciones del sistema
from django.urls import path
from .views import *
app_name = "mutual"

urlpatterns = [
    path('crearMutual/',MutualCreateView.as_view(), name="mutual_crear"),
    path('mutuales/listado', MutualesListView.as_view(), name="listado_mutual"),
    path('mutuales/editar/<int:pk>', EditarMutal, name="editar_mutual"),

    path('declaracionjurada/crear/<str:accion>/', DeclaracionJuradaCreateView.as_view(), name="declaracion_jurada"),
    path('declaracionjurada/historialDeclarado',DeclaracionJuradaDeclaradoListView.as_view(), name="declaracion_jurada_declarado_listado"),
    
    path('declaracionjurada/leer',leerDeclaracionJurada , name="leer_declaracion_jurada"),
    path('verificar_todas_leidas/<int:periodo_pk>/', verificar_todas_leidas, name='verificar_declaraciones_todas_leidas'),

    path('declaracionjurada/historico',HistoricoView.as_view(), name="historico"),
    path('DeclaracionJurada/<int:pk>/', descargarDeclaracion, name="descargarDeclaracion"),
    path('DeclaracionJurada/archivo/<int:pk>/', descargarArchivo, name="descargarArchivo"),

    path('periodos/periodo/crear', PeriodoCreateView.as_view(), name="periodo_crear"),
    path('periodos/periodo/vigente', periodoVigenteDetalle , name="periodo_vigente_detalle"),
    path('periodos/periodo/vigente/<int:pk>/mutuales/nopresentaron', periodoVigenteMutualNoPresento , name="mutual_no_presento"),
    path('periodos/periodo/vigente/<int:pk>/finalizar', finalizarPeriodo , name="finalizar_periodo"),
    path('periodos/periodo/vigente/<int:pk>/finalizar_crear_nuevo', finalizarPeriodoCrearNuevo , name="finalizar_periodo_crear_nuevo"),

    path('exito/', mutual_exito, name='mutual_exito'),
    path('prueba/', tu_vista, name='t_vista'),
    path('datos/', DetalleMutualView.as_view(), name='detalles_mimutual'),
    path('confirmacion/', ConfirmacionView.as_view(), name='confirmacion'),
    path('visualizar_errores/', VisualizarErroresView.as_view(), name='visualizarE'),
    path('msj_informativo/', MsjInformativo.as_view(), name='msj_info'),
    path('actualizar/<int:pk>/', MutualUpdateView.as_view(), name='actualizar'),

]
