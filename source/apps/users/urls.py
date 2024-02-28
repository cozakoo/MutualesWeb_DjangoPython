from django.shortcuts import render
from .views import CustomLoginView, RegisterUserMutalView, register_user_mutual_exito , cerrar_session
from django.urls import path

app_name = "users"

urlpatterns = [
  path('login/', CustomLoginView.as_view(), name='login'),
  path('cerrar_session/',cerrar_session,name='cerrar_session'),  
  path('registerM/', RegisterUserMutalView.as_view(), name='register'), 
  # path('registerE/', RegisterUserMutalView.as_view(), name='register'), 
  path('exitoM/', register_user_mutual_exito, name='register_userM_exito'),
]

