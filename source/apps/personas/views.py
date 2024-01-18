from django.shortcuts import render
from django.views.generic.edit import CreateView
from .models import *
from .forms import  FormularioPersona
from django.contrib import messages

# Create your views here.
class PersonaCreateView(CreateView):
    model = Persona
    form_class = FormularioPersona
    template_name = "alta_persona.html"

            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['rol_persona'] = FormRol(prefix='d_prestamo')
        return context
    
    
 