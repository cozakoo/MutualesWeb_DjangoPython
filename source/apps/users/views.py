from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, RegisterUserMutualForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .views import LoginView
from ..clientes.models import Cliente
from ..personas.models import Persona
from ..mutual.models import Mutual
from ..empleadospublicos.models import EmpleadoPublico

from .models import UserRol
from django.contrib.auth.models import User,Permission
from django.db import transaction
from django.contrib.auth import logout
        
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def obtenerPermiso(name):
# Precondicion: {name} Exits in {"administador","cliente","empleadoPublico"}
        
        # if name == "administrador":
        #     content_type = ContentType.objects.get_for_model(Cliente)
        #     permiso, creado = Permission.objects.get_or_create(
        #         codename='permission_admin',
        #         name='Control total administrador',
        #         content_type=content_type,
        #     )
        #     return permiso
        
        if name == "cliente":
            content_type = ContentType.objects.get_for_model(Cliente)
            permiso, creado = Permission.objects.get_or_create(
                codename='permission_cliente_mutual',
                name='Control total cliente Mutual',
                content_type=content_type,
            )
            return permiso
        
        if name == "empleadoPublico":
            content_type = ContentType.objects.get_for_model(EmpleadoPublico)
            permiso, creado = Permission.objects.get_or_create(
                codename='permission_empleado_publico',
                name='Control total empleado publico',
                content_type=content_type,
            )
            return permiso
        
        
        
        
        
def cerrar_session(request):
    logout(request)
    
    return redirect('users:login')


class CustomLoginView(LoginView):
    template_name = 'login_acceso.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('mutualWeb:dashboard')
    
class RegisterUserMutalView(CreateView):
    template_name ='registrar_usuario_mutual.html'
    form_class = RegisterUserMutualForm
    success_url = reverse_lazy('users:register_userM_exito')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro Usuario Mutual'
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if not form.is_valid():
            return self.form_invalid(form)
        else:
            return self.form_valid(form)
          
    def form_valid(self,form):
        # Verifica si el correo electrónico no contiene el símbolo "@"
        if 'email' in form.errors and 'El correo electrónico debe incluir un signo @.' in form.errors['email']:
            messages.error(self.request, 'El correo electrónico debe incluir un signo @.')
            return super().form_invalid(form)
        else:
            print("SOOOOY EL FORM ")
            print(form)
            print("SOY username")
            print(form.cleaned_data["username"])
         
            correo = form.cleaned_data["email"]
        #  with transaction.atomic(): 
            p = Persona(
                correo = correo,
                es_cliente = True
            )
            
            p.save()
            
            nombre = form.cleaned_data["mutual"]
            e = Mutual.objects.get(nombre = nombre)
            
            
            c = Cliente (
                persona = p,
                mutual = e,
                tipo = Cliente.TIPO
            )
            
            c.register
            c.save()
            
            permiso, creado = Permission.objects.get_or_create(
                                                                codename='add_declaracionjurada',
                                                                name='Can add declaracion jurada',
                                                              )
            
            
            form.save() 
            
            user = User.objects.get(username=form.cleaned_data["username"])
            
            
            user.user_permissions.add(permiso)
            permiso = obtenerPermiso("cliente")
            user.user_permissions.add(permiso)
            
            
            
            UserRol.objects.create(user = user , rol = c)
             
            
            print("pude añadir permiso")
            return super().form_valid(form)
        
    def form_invalid(self, form):
        print("Errores del formulario en form_invalid:", form.errors)
        return super().form_invalid(form)
    
def register_user_mutual_exito(request):
    return render(request,'registrar_usuario_mutual_exito.html')




class RegistereEmpleadoPublicoView(CreateView):
    template_name ='registrar_usuario_empleado_publico.html'
    form_class = RegisterUserMutualForm
    success_url = reverse_lazy('users:register_userM_exito')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro Usuario Mutual'
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if not form.is_valid():
            return self.form_invalid(form)
        else:
            return self.form_valid(form)
          
          
    def form_valid(self,form):
        # Verifica si el correo electrónico no contiene el símbolo "@"
        if 'email' in form.errors and 'El correo electrónico debe incluir un signo @.' in form.errors['email']:
            messages.error(self.request, 'El correo electrónico debe incluir un signo @.')
            return super().form_invalid(form)
        else:
            print("SOOOOY EL FORM ")
            print(form)
            print("SOY username")
            print(form.cleaned_data["username"])
         
            correo = form.cleaned_data["email"]
        #  with transaction.atomic(): 
            p = Persona(
                correo = correo,
                es_empleado_publico = True
            )
            
            p.save()
            
            
            e =  EmpleadoPublico(
                persona = p,
                tipo = EmpleadoPublico.TIPO
            )
            
            e.register
            e.save()
            
            
            form.save() 
            
            user = User.objects.get(username=form.cleaned_data["username"])
            
            permiso = obtenerPermiso("empleadoPublico")
            user.user_permissions.add(permiso)
            
            UserRol.objects.create(user = user , rol = e)
             
            
            print("pude añadir permiso")
            return super().form_valid(form)
        
    def form_invalid(self, form):
        print("Errores del formulario en form_invalid:", form.errors)
        return super().form_invalid(form)
         
         
         