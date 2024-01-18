from django.shortcuts import render
from .views import CustomLoginView, RegisterUserMutalView
from django.urls import path

app_name = "users"

urlpatterns = [
  path('login/', CustomLoginView.as_view(), name='login'),  
  path('registerM/', RegisterUserMutalView.as_view(), name='register'), 
]

