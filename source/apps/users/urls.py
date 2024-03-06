from django.shortcuts import render
from .views import CustomLoginView, RegisterUserMutalView, register_user_mutual_exito , cerrar_session , RegistereEmpleadoPublicoView , Menu,RegistereAdministradorView
from django.urls import path

app_name = "users"

urlpatterns = [
  path('login/', CustomLoginView.as_view(), name='login'),
  path('cerrar_session/',cerrar_session,name='cerrar_session'),
  path('menu_usuario/', Menu.as_view(), name='menu_user'),  
  path('register_user_mutual/', RegisterUserMutalView.as_view(), name='register_U_M'), 
  path('register_user_empl_publico/', RegistereEmpleadoPublicoView.as_view(), name='register_E_P'),
  path('register_user_administrador/', RegistereAdministradorView.as_view(), name='register_A'),
  path('exitoM/', register_user_mutual_exito, name='register_userM_exito'),
  
]

