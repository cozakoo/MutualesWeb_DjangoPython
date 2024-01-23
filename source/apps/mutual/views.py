from typing import Any
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView
from .models import Mutual , DetalleMutual , DeclaracionJurada
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.core.files.base import ContentFile
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

import linecache
import sys
import re




# Create your views here.


    
def tu_vista(request):
    data = Mutual.objects.all()
    return render(request, 'tu_vista.html', {'data': data})
  

from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz
from django.utils.translation import gettext as _
from datetime import date


class DeclaracionJuradaCreateView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = '/login/'  # Puedes personalizar la URL de inicio de sesión
    # permission_required = 'nombre_app.puede_realizar_accion'
    permission_required = 'mutual.add'
    model = DeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"
    success_url = reverse_lazy('mutual:mutual_exito')
    LONGITUD_RECLAMO = 57
    LONGITUD_PRESTAMO = 54
    
    def get_success_url(self):
        # Obtener la URL a la que se debe redirigir después del éxito
        return reverse_lazy('dashboard')
    
    # def post(self, request, *args, **kwargs):
    #     return form_valid(self, form)
          
        
    def obtener_mes_y_anio_actual(self):
        # Encontrar la zona horaria basada en la ubicación
        tz_finder = TimezoneFinder()
        ubicacion = tz_finder.timezone_at(lng=-64.1428, lat=-31.4201)  # Coordenadas de Buenos Aires

        # Obtener la fecha y hora actual en la zona horaria de Buenos Aires
        zona_horaria_argentina = pytz.timezone(ubicacion)
        fecha_hora_actual = datetime.now(zona_horaria_argentina)

        # Obtener el mes y el año actual de forma dinámica en español
        mes_actual = fecha_hora_actual.strftime('%B')
        mes_actual = _(mes_actual)  # Traducir el nombre del mes
        año_actual = fecha_hora_actual.strftime('%Y')
        
        # Devolver el mes y el año en un solo string
        return f'{mes_actual} del {año_actual}'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mes_y_anio_actual = self.obtener_mes_y_anio_actual()
        context['titulo'] = f'Cargar Declaración Jurada para {mes_y_anio_actual}'
        return context

    def es_numerico(self, cadena):
        """Verifica si una cadena está compuesta solo por dígitos."""
        return bool(re.match("^\d+$", cadena))

    def form_valid(self, form):
        """Maneja la validación del formulario antes de guardarlo."""
        tipo = form.cleaned_data['tipo']
        archivo = form.cleaned_data['archivos']

        try:
            with transaction.atomic():
                if tipo == 'P':
                    archivo_valido = self.validar_prestamo(form, archivo)
                else:
                    archivo_valido = self.validar_reclamo(form, archivo)

                if archivo_valido:
                    print("MI ARCHIVO ES VALIDO")
                    # Obtener el mes y el año actual
                    mes_actual = self.obtener_mes_y_anio_actual()

                    # Establecer el valor del campo periodo (Ejemplo: "Enero del 2024")
                    form.instance.periodo = f"{mes_actual} "

                    # Establecer la fecha de subida
                    form.instance.fecha_subida = date.today()
                    primera_mutual = Mutual.objects.first()
                    form.instance.mutual = primera_mutual
                    
                    form.instance.archivo = form.cleaned_data['archivos']
                    
                    
                    return super().form_valid(form)                    
                                            
                else:
                     print("es invalido")
                     return super().form_invalid(form)
                    
        except Exception as e:
            messages.error(self.request, f"Error al procesar el formulario: {e}")
            return self.form_invalid(form)

    def validar_reclamo(self, form, archivo):
        """Valida el contenido del archivo de RECLAMO."""
        print("-----  VALIDANDO  RECLAMO  -------")
        print("")
        todas_las_lineas_validas = True  # Variable para rastrear si todas las líneas son válidas
        
        try:
                file = archivo.open()
                for line_number, line_content_bytes in enumerate(file, start=1):
                    line_content = line_content_bytes.decode('utf-8').rstrip('\r\n')
                    print(f"Línea {line_number}: {line_content}")
                    
                    # Verificar la longitud de la línea incluyendo espacios en blanco y caracteres de nueva línea
                    if len(line_content) != self.LONGITUD_RECLAMO:
                        todas_las_lineas_validas = False
                        break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                    else:
                        self.validar_numero(line_content, line_number, 3, 16, "DOCUMENTO")
                        self.validar_numero(line_content, line_number, 16, 20, "CONCEPTO")
                        self.validar_numero(line_content, line_number, 20, 31, "IMPORTE")
                        self.validar_fecha(line_content, line_number, 31, 39, "FECHA INICIO")
                        self.validar_fecha(line_content, line_number, 39, 47, "FECHA FIN")
                        self.validar_numero(line_content, line_number, 47, 54, "CUPON")
                        self.validar_numero(line_content, line_number, 54, 57, "CUOTA")
                    print("")
            
             # Después de procesar todas las líneas, mostrar el mensaje correspondiente
                if todas_las_lineas_validas:
                    mensaje_error = "Reclamo cargado correctamente"
                    messages.success(self.request, mensaje_error)
                else:
                    mensaje_error = f"Error: Todas las líneas del archivo deben tener {self.LONGITUD_RECLAMO} caracteres."
                    messages.warning(self.request, mensaje_error)
                    return False
        
        except Exception as e:
          messages.error(self.request, f"Error al leer el archivo: {e}")
          return False
        

    def validar_numero(self, line_content, line_number, inicio, fin, tipo_numero):
        """Valida un número en una línea."""
        numero = line_content[inicio:fin]
        mensaje = f"{tipo_numero}: {numero}"
        print(mensaje)

        if not self.es_numerico(numero):
            mensaje_error = f"Error: La línea {line_number}. {mensaje} tiene caracteres no numéricos. Línea: {line_content}"
            messages.warning(self.request, mensaje_error)

    def validar_fecha(self, line_content, line_number, inicio, fin, tipo_fecha):
        fecha_str = line_content[inicio:fin]
        mensaje = f"{tipo_fecha}: {fecha_str}"
        print(mensaje)

        try:
            # Convertir la cadena de fecha a un objeto de fecha
            fecha_obj = datetime.strptime(fecha_str, "%d%m%Y").date()
            print(fecha_obj)

            # Obtener la fecha actual
            fecha_actual = date.today()

            # Obtener el mes y el año de la fecha de la línea
            mes_fecha = fecha_obj.month
            anio_fecha = fecha_obj.year

            # Comparar si la fecha de la línea está dentro del mismo mes que la fecha actual
            if fecha_obj.month != fecha_actual.month or fecha_obj.year != fecha_actual.year:
                mensaje_error = f"Error: La {tipo_fecha} en la línea {line_number} no está dentro del mes actual. Línea: {line_content}"
                messages.warning(self.request, mensaje_error)

        except ValueError:
            mensaje_error = f"Error: La {tipo_fecha.lower()} en la línea {line_number} no es válida. Línea: {line_content}"
            messages.warning(self.request, mensaje_error)


    def validar_prestamo(self, form, archivo):
        """Valida el contenido del archivo de PRESTAMO."""
        print("-----  VALIDANDO  PRESTAMO  -------")
        print("")
        todas_las_lineas_validas = True  # Variable para rastrear si todas las líneas son válidas

        try:
                file = archivo.open() 
                for line_number, line_content_bytes in enumerate(file, start=1):
                    line_content = line_content_bytes.decode('utf-8').rstrip('\r\n')
                    print(f"Línea {line_number}: {line_content}")
                    
                    # Verificar la longitud de la línea incluyendo espacios en blanco y caracteres de nueva línea
                    if len(line_content) != self.LONGITUD_PRESTAMO:
                        todas_las_lineas_validas = False
                        break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                    else:
                        self.validar_numero(line_content, line_number, 3, 16, "DOCUMENTO")
                        self.validar_numero(line_content, line_number, 16, 20, "CONCEPTO")
                        self.validar_numero(line_content, line_number, 20, 31, "IMPORTE")
                        self.validar_fecha(line_content, line_number, 31, 39, "FECHA INICIO")
                        self.validar_fecha(line_content, line_number, 39, 47, "FECHA FIN")
                        self.validar_numero(line_content, line_number, 47, 54, "CUPON")
                    print("")
            
            # Después de procesar todas las líneas, mostrar el mensaje correspondiente
                    if todas_las_lineas_validas:
                        mensaje_error = "Prestamo cargado correctamente"
                        messages.success(self.request, mensaje_error)
                        return True
                    else:
                        mensaje_error = f"Error: Todas las líneas del archivo deben tener {self.LONGITUD_RECLAMO} caracteres."
                        messages.warning(self.request, mensaje_error)
                        return False

        except Exception as e:
                    messages.error(self.request, f"Error al leer el archivo: {e}")
                    return False
        
class MutualCreateView(CreateView):
    model = Mutual
    form_class = FormularioMutual
    template_name = 'mutual_alta.html'
    success_url = reverse_lazy('mutual:mutual_exito')
    
    def form_invalid(self, form):
        form.error.clear()
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.method == 'POST':
            context['detalle_prestamo'] = FormDetalle(self.request.POST, prefix='d_prestamo')
            context['detalle_reclamo'] = FormDetalle(self.request.POST, prefix='d_reclamo')
        else:
            context['detalle_prestamo'] = FormDetalle(prefix='d_prestamo')
            context['detalle_reclamo'] = FormDetalle(prefix='d_reclamo')

        context['titulo'] = 'Alta de Mutual'
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