from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm

def dashboard(request):
    return render(request, 'dashboard.html')

class CustomLoginView(LoginView):
    form_class = CustomLoginForm