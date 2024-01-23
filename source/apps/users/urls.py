from django.shortcuts import render
from .views import CustomLoginView, RegisterUserMutalView, register_user_mutual_exito
from django.urls import path

app_name = "users"

urlpatterns = [
  path('login/', CustomLoginView.as_view(), name='login'),  
  path('registerM/', RegisterUserMutalView.as_view(), name='register'), 
  path('exitoM/', register_user_mutual_exito, name='register_userM_exito'),
]

