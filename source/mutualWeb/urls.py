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
from mutualWeb.views import *
from .views import *

urlpatterns = [
    #PRIINCIPALES
    path('', RedirectView.as_view(url='dashboard/', permanent=False), name='index'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('dashboard/', dashboard, name='dashboard'),

    #APLICACIONES
    path('dashboard/clientes/', include('apps.clientes.urls')),
    path('dashboard/mutual/', include('apps.mutual.urls')),
]
