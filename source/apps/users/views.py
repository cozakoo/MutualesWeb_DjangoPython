from datetime import timezone
from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.views import View
from mutualWeb import forms
from mutualWeb.utils.mensajes import mensaje_error, mensaje_exito
from ..administradores.models import Administrador
from .forms import CustomLoginForm, CustomPasswordChangeForm, RegisterUserMutualForm, RegisterUserEmpleadoPublicoForm, UserFilterForm
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
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import permission_required, login_required


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
            name='Control total empleado público',
            content_type=content_type,
        )
        return permiso

def cerrar_session(request):
    userRol = UserRol.objects.get(user = request.user )
    userRol.ultimaConexion = request.user.last_login
    userRol.save()
    logout(request)
    return redirect('users:login')

@login_required(login_url="/login/")
@permission_required('administradores.permission_administrador', raise_exception=True)
def cambiarEstado(request, pk):
    if request.method == 'POST':
        try:
            user = User.objects.get(pk = pk)
            estado = user.is_active
            user.is_active = not estado 
            user.save()
            messages.success(request, "Estado del usuario: "+ str(User.username) +" cambiado.")
        except User.DoesNotExist:
            print("no cambiado")
    return redirect('users:usuarios_listado')

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
        if not self.request.user.is_active :
           messages.error(self.request, 'Usuario Inactivo, loggeo no permitido')
           return redirect('users:login')
        return super().form_invalid(form)
    
    
class RegisterUserMutalView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name ='registrar_usuario_mutual.html'
    form_class = RegisterUserMutualForm
    success_url = reverse_lazy('users:register_U_M')
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
                e = Mutual.objects.get(alias = nombre)

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
        context['titulo'] = 'Registro de Usuario Empleado Público'
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
              




        
class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    model = User
    template_name ='listado_usuarios.html'
    paginate_by = 12
    permission_required = "administradores.permission_administrador"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_form = UserFilterForm(self.request.GET)

        if filter_form.is_valid():
            username = filter_form.cleaned_data.get('username')
            is_active_values = filter_form.cleaned_data.get('is_active')  # Obtenemos los valores seleccionados

            if username:
                queryset = queryset.filter(username__icontains=username)

            if is_active_values:
                # Convertimos los valores seleccionados a booleanos
                is_active_values = [bool(int(value)) for value in is_active_values]
                queryset = queryset.filter(is_active__in=is_active_values)

        return queryset.order_by('-is_active', 'username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Usuarios'
        context['filter_form'] = UserFilterForm(self.request.GET)
        return context

@login_required(login_url="/login/")
@permission_required('administradores.permission_administrador', raise_exception=True)
def PasswordChangeAdmnistrador(request, pk):
    
    if request.method == 'POST':
           data = request.POST  
           password = data.get('password')
           try:
                user = User.objects.get(pk = pk)   
                user.set_password(password)
                user.save()
                messages.success(request,"contraseña cambiada correctamente")
                
           except User.DoesNotExist:
               messages.error(request,"no se pude completar operacion")

    return redirect('users:usuarios_listado')
    

    
    

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'cambiar_password.html'  # Template donde mostrar el formulario
    success_url = reverse_lazy('dashboard')
    login_url = '/login/'
    
    def form_valid(self, form):
        mensaje_exito(self.request, f'Contraseña cambiada con exito.')
        return super().form_valid(form)