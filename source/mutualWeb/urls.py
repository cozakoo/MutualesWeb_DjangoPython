"""
URL configuration for mutualWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from mutualWeb.views import *
from .views import *
from mutualWeb import views



urlpatterns = [
    #PRIINCIPALES
    # path('', bienvenida , name='index'),
    path('', RedirectView.as_view(url='login/', permanent=False), name='index'),
    path('admin_manager_ministerio/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),

    #APLICACIONES
    path('dashboard/clientes/', include('apps.clientes.urls')),
    path('dashboard/mutual/', include('apps.mutual.urls')),
    path('dashboard/personas/', include('apps.personas.urls')),
    path('', include('apps.users.urls')),
    path('home/app_reportes/',include('apps.reportes.urls')),

    path("selectable/", include("selectable.urls")),
    path('buscar_mutuales/', views.buscar_mutuales, name='buscar_mutuales'),
    
    # para abir los manuales
    path('manual_usuario_mutual/', abrirManualMutual, name="pdf_manual_mutual"),
    path('manual_usuario_operativos/', abrirManualOperativos, name="pdf_manual_operativos"),
    path('manual_usuario_administrador/', abrirManualAdministrador, name="pdf_manual_administrador"),
]

handler404 = "mutualWeb.views.pagina_no_encontrada"
