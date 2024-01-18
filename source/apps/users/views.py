from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, RegisterUserMutualForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .views import LoginView
from ..clientes.models import Cliente
from ..personas.models import Persona
from ..mutual.models import Mutual


# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'login_acceso.html'
    form_class = CustomLoginForm
    
class RegisterUserMutalView(CreateView):
    template_name ='registrar_usuario_mutual.html'
    form_class = RegisterUserMutualForm
    
    def post(self, request, *args, **kwargs):
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if not form.is_valid:
                return self.form_invalid()
            else:
                return self.form_valid(form)
            
    def form_valid(self,form):
         print("SOOOOY EL FORM ")
         print(form)
         print("SOY username")
         print(form.cleaned_data["username"])
         
         p = Persona(
              username=form.cleaned_data["username"],
              clave=form.cleaned_data["password1"],
              correo = form.cleaned_data["email"],
              es_cliente = True
         )
         
         p.save()
        
         nombre = form.cleaned_data["mutual"]
         e = Mutual.objects.get(nombre = nombre)
        
         
         c = Cliente (
             persona = p,
             mutual = e
           )
         c.save()
         
         return super().form_valid(form)
         
         
         