from .models import *
from .forms import *
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
# Create your views here.
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = FormularioCliente
    template_name = 'cliente_alta.html'
    success_url = reverse_lazy('clientes:confirmacion_cliente')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

def confirmacion_cliente(request):
    return render(request, 'confirmacion_cliente.html')
