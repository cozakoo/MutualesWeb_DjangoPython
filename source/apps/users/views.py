from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views import View
from mutualWeb.utils.mensajes import mensaje_error, mensaje_exito
from ..administradores.models import Administrador
from .forms import CustomLoginForm, RegisterUserMutualForm, RegisterUserEmpleadoPublicoForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from .views import LoginView
from ..clientes.models import Cliente
from ..personas.models import Persona
from ..mutual.models import Mutual
from ..empleadospublicos.models import EmpleadoPublico
from .models import UserRol
from django.contrib.auth.models import User,Permission
from django.db import transaction
from django.contrib.auth import logout
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.http import JsonResponse


def obtenerPermiso(name):
    # Precondicion: {name} Exits in {"administador","cliente","empleadoPublico"}
    if name == "administrador":
        content_type = ContentType.objects.get_for_model(Administrador)
        permiso, creado = Permission.objects.get_or_create(
            codename='permission_administrador',
            name='Control total administrador',
            content_type=content_type,
        )
        return permiso
    
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

def register_user_mutual_exito(request):
    return render(request,'registrar_usuario_mutual_exito.html')

class Menu(LoginRequiredMixin,PermissionRequiredMixin,TemplateView):
    template_name = 'menu.html'
    success_url = '/menu_user/'
    login_url = '/login/'
    permission_required = "administradores.permission_administrador"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Creación de usuarios'
        return context


class CustomLoginView(LoginView, View):
    template_name = 'login_acceso.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('mutualWeb:dashboard')
    
    def get(self, request, *args: str, **kwargs):
        if request.user.is_authenticated:
           return redirect('dashboard')
        return super().get(request, *args, **kwargs)
    
    def form_invalid(self, form):
        mensaje_error(self.request, '')
        return super().form_invalid(form)
    
class RegisterUserMutalView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name ='registrar_usuario_mutual.html'
    form_class = RegisterUserMutualForm
    success_url = reverse_lazy('users:usuarios_listado')
    login_url = '/login/'
    permission_required = "administradores.permission_administrador"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro de usuario para una Mutual'
        
        mutuales = Mutual.objects.all().filter(activo=True)
        context['mutuales'] = mutuales

        return context
    

          
    def form_valid(self,form):
        # Verifica si el correo electrónico no contiene el símbolo "@"

  
        correo = form.cleaned_data["email"]
        try:
            with transaction.atomic():
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
                form.save() 
                
                user = User.objects.get(username=form.cleaned_data["username"])
                permiso = obtenerPermiso("cliente")
                user.user_permissions.add(permiso)
                UserRol.objects.create(user = user , rol = c)                
                mensaje_exito(self.request, f'Usuario creado para una mutual con exito.')                
                return super().form_valid(form)
        except Exception:   
            mensaje_error(self.request, f'No se pudo crear el usuario')
            return super().form_invalid(form)
            
            



class RegistereEmpleadoPublicoView(LoginRequiredMixin, PermissionRequiredMixin , CreateView):
    template_name ='registrar_usuario.html'
    form_class = RegisterUserEmpleadoPublicoForm
    success_url = reverse_lazy('users:usuarios_listado')
    login_url = '/login/'
    permission_required = "administradores.permission_administrador"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro de Usuario Empleado Publico'
        return context
    
   
          
    def form_valid(self,form):

     
            correo = form.cleaned_data["email"]
            try:   
                with transaction.atomic(): 
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
                    mensaje_exito(self.request, f'Usuario creado con exito.')                

                    return super().form_valid(form)
            except Exception:
               mensaje_error(self.request, f'No se pudo crear el usuario')
               return super().form_invalid(form)
                
   

class RegistereAdministradorView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
        template_name ='registrar_usuario.html'
        form_class = RegisterUserEmpleadoPublicoForm
        success_url = reverse_lazy('users:usuarios_listado')
        login_url = '/login/'
        permission_required = "administradores.permission_administrador"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['titulo'] = 'Registro Usuario Adminsitrador'
            return context
            
            
        def form_valid(self,form):
            # Verifica si el correo electrónico no contiene el símbolo "@"
            if 'email' in form.errors and 'El correo electrónico debe incluir un signo @.' in form.errors['email']:
                messages.error(self.request, 'El correo electrónico debe incluir un signo @.')
                return super().form_invalid(form)
            else:
                correo = form.cleaned_data["email"]
                try:   
                    with transaction.atomic():           
                        p = Persona(
                            correo = correo,
                            es_admin = True
                        )
                        
                        p.save()
                        e =  Administrador(
                            persona = p,
                            tipo = Administrador.TIPO
                        )
                        e.register
                        e.save()
                        form.save() 
                        user = User.objects.get(username=form.cleaned_data["username"])
                        permiso = obtenerPermiso("administrador")
                        user.user_permissions.add(permiso)
                        permiso = obtenerPermiso("empleadoPublico")
                        user.user_permissions.add(permiso)
                      
                        UserRol.objects.create(user = user , rol = e)
                        mensaje_exito(self.request, f'Usuario creado con exito.')                
                        return super().form_valid(form)
                except Exception:
                  mensaje_error(self.request, f'No se pudo crear el usuario')
                  return super().form_invalid(form)
              
        


class UserListView(ListView):
    model = User
    template_name ='listado_usuarios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de usuarios'
        return context






class CambiarPasswordView(LoginRequiredMixin, FormView):

    def post(self, request, user_id):
        # Obtener el usuario específico
        usuario = get_object_or_404(User, id=user_id)

        # Obtener la nueva contraseña del formulario (en este ejemplo, asumimos que la contraseña se pasa en el cuerpo de la solicitud)
        nueva_password = request.POST.get('nueva_password')

        # Cambiar la contraseña del usuario
        usuario.set_password(nueva_password)
        usuario.save()

        return JsonResponse({'mensaje': 'Contraseña cambiada con éxito'})


