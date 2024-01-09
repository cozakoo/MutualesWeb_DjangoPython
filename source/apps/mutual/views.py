from django.shortcuts import render
from django.views.generic.edit import CreateView
from .models import Mutual
from .forms import *

# Create your views here.
class MutualCreateView(CreateView):
    model = Mutual
    form_class = FormularioMutual
    template_name = 'Mutual_alta.html'
   

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['titulo'] = "Alta de cliente"
    #     return context