from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from apps.users.models import UserRol
from django.contrib.auth.models import User



@login_required(login_url='users:login')

# @permission_required(".add_choice", raise_exception=True)
def dashboard(request):
    userRol = UserRol.objects.get(user = request.user )
    contexto = {
        'rol': userRol.rol,
        'ultimaSession':request.user.last_login,
    }
     
    if  userRol.rol.persona.es_cliente: 
     return render(request, 'dashboardCliente.html',contexto)
     
    if  userRol.rol.persona.es_empleado_publico: 
     return render(request, 'dashboardEmpleadoPublico.html',contexto)
 
    if userRol.rol.persona.es_admin:
        return render(request, 'dashboardAdministrador.html',contexto)
             





# class CustomLoginView(LoginView):
#     form_class = CustomLoginForm