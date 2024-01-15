from django.forms import ValidationError
from django.shortcuts import render
from django.views.generic.edit import CreateView
from .models import Mutual , DetalleMutual , DeclaracionJurada
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages


class DeclaracionJuradaCreateView(CreateView):
    model = DeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"
    success_url = reverse_lazy('mutual:mutual_exito')

    def form_valid(self, form):
        tipo = form.cleaned_data['tipo']
        print("TIPO")
        print(tipo)
        # Asigna valores a los campos de fecha antes de guardar
        # Procesar el archivo aquí
        archivo = form.cleaned_data['archivo']
        if tipo == 'P':
            self.validar_prestamo(form, archivo)
        else:
            self.validar_reclamo(form, archivo)
        # Guardar el formulario
        response = super().form_valid(form)
        # Puedes realizar acciones adicionales después de guardar el formulario si es necesario
        return response

    def validar_prestamo(self, form, archivo):
        # print("Validando préstamo")
        # try:
            # Imprimir contenido del archivo
        print("ESTOY LEYENDO EL ARCHIVO:")
            # with archivo.open() as file:
                # content = file.read()
                # print(content)
            # Agregar lógica de validación del archivo aquí
            # Por ejemplo, verifica el formato, tamaño, contenido, etc.
            # Devuelve True si el archivo es válido
            # return True
        # except Exception as e:
            # Si ocurre algún error al intentar leer el archivo
            # print(f"Error al leer el archivo: {e}")
            # raise ValidationError("Error al procesar el archivo.")
        # Puedes acceder a otros campos del formulario si es necesario
        # monto = form.cleaned_data['monto']
        # Realiza la validación según tus necesidades

    def validar_reclamo(self, form, archivo):
        # Agrega lógica de validación específica para tipo distinto de 'P' aquí
        print("Validando reclamo")
        # Puedes acceder a otros campos del formulario si es necesario
        # motivo = form.cleaned_data['motivo']
        # Realiza la validación según tus necesidades

class MutualCreateView(CreateView):
    model = Mutual
    form_class = FormularioMutual
    template_name = 'Mutual_alta.html'
    success_url = reverse_lazy('mutual:mutual_exito')
    
    def form_invalid(self, form):
        form.error.clear()
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalle_prestamo'] = FormDetalle(prefix='d_prestamo')
        context['detalle_reclamo'] = FormDetalle(prefix='d_reclamo')    
        return context 
    
   
   
    def post(self, request, *args, **kwargs):
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            detalle_reclamo  = FormDetalle(request.POST, prefix='d_reclamo')
            detalle_prestamo = FormDetalle(request.POST, prefix='d_prestamo')
            

            if form.is_valid() and detalle_prestamo.is_valid() and detalle_reclamo.is_valid():
                return self.form_valid(form, detalle_reclamo, detalle_prestamo)
            else:
                print("LLLLLLLLLLformularios invalidosLLLLLLLLL")
    
    
    def form_valid(self, form, d_reclamo, d_prestam):
            
            campo_existente = form.cleaned_data['cuit']
            if Mutual.objects.filter(cuit = campo_existente).exists():
                messages.error(self.request,"El cuit ya existe")
                return self.render_to_response(self.get_context_data(form=form))
        
        
 
            # Si no existe, guarda el objeto y realiza las acciones necesarias
      
            m = Mutual(nombre=form.cleaned_data["nombre"],
                      cuit=form.cleaned_data["cuit"],
                      activo = True,
                      )
            m.save()
            m.detalle.create(
                tipo = "P",
                origen = d_prestam.cleaned_data['origen'],
                destino = d_prestam.cleaned_data['destino'],
                concepto_1 = d_prestam.cleaned_data['concep1'],
                concepto_2 = d_prestam.cleaned_data['concep2'],
            )
       
          
            m.detalle.create(
                tipo = "R",
                origen = d_reclamo.cleaned_data['origen'],
                destino = d_reclamo.cleaned_data['destino'],
                concepto_1 = d_reclamo.cleaned_data['concep1'],
                concepto_2 = d_reclamo.cleaned_data['concep2'],
            )
        
            
            return super().form_valid(form)
   
def mutual_exito(request):
    return render(request,'mutual_exito.html')
  
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['titulo'] = "Alta de cliente"
    #     return context