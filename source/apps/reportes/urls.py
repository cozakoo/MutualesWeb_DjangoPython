from django.urls import path

from apps.reportes.views import *

app_name="reportes"


urlpatterns = [
path('reportes/mutual/declaracionesjuradas/<int:mutual_id>/', reporteMutualDeclaracionesJuradasView.as_view(), name="reporte_mutual_declaraciones"),
]
