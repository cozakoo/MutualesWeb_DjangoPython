from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from apps.users.models import UserRol
from django.contrib.auth.models import User

# # @login_required(login_url='login')
# @login_required
# @permission_required(".add_choice", raise_exception=True)
def dashboard(request):
    userRol = UserRol.objects.get(user = request.user )
    contexto = {
        'rol': userRol.rol,
        'ultimaSession':request.user.date_joined,
    }
     
    if  userRol.rol.persona.es_cliente: 
     return render(request, 'dashboardCliente.html',contexto)


# class CustomLoginView(LoginView):
#     form_class = CustomLoginForm