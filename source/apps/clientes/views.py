from .models import *
from .forms import *
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

# Create your views here.
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = FormularioCliente
    template_name = 'cliente_alta.html'
    success_url = reverse_lazy('afiliados:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = "Alta de cliente"
        return context