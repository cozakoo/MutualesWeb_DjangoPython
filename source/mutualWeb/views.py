from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required

# # @login_required(login_url='login')
# @login_required
# @permission_required(".add_choice", raise_exception=True)
def dashboard(request):
    return render(request, 'dashboard.html')


def bienvenida(request):
    return render(request, 'dashboard.html')


# class CustomLoginView(LoginView):
#     form_class = CustomLoginForm