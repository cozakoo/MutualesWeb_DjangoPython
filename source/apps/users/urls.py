from django.shortcuts import render
from .views import *
from django.urls import path

app_name = "users"

urlpatterns = [
  path('login/', CustomLoginView.as_view(), name='login'),
  path('cerrar_session/',cerrar_session,name='cerrar_session'),

  path('usuarios/listado', UserListView.as_view(), name='usuarios_listado'),
  path('usuarios/menu/', Menu.as_view(), name='menu_user'), 
  path('usuarios/usuario/mutual/crear', RegisterUserMutalView.as_view(), name='register_U_M'), 
  path('usuarios/usuario/emplpublico/crear', RegistereEmpleadoPublicoView.as_view(), name='register_E_P'),
  path('usuarios/usuario/administrador/crear', RegistereAdministradorView.as_view(), name='register_A'),
  path('cambiar-password/', CustomPasswordChangeView.as_view(), name='cambiar_password'),
  # path('usuarios/usuario/cambiarcontrasenia', CambiarPasswordViewUsers.as_view(), name='cambiar_contrasena'),
  
  # path('exitoM/', register_user_mutual_exito, name='register_userM_exito'),
]

