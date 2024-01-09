# Importaciones del sistema
from django.urls import path
from .views import MutualCreateView

app_name = "mutual"

urlpatterns = [
    path('crear/',MutualCreateView.as_view(), name="mutual_crear"),
]