from django.urls import path
from .views import *

app_name="personas"

urlpatterns = [
    path('crear/',PersonaCreateView.as_view(), name="persona_crear"),
]


