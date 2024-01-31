from typing import Any
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView 
from django.views.generic import DetailView
from .models import Mutual , DetalleMutual , DeclaracionJurada
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.core.files.base import ContentFile
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from ..users.models import UserRol
import linecache
import sys
import re
import locale
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import calendar
from timezonefinder import TimezoneFinder
import pytz
from django.utils.translation import gettext as _
from datetime import date

def tu_vista(request):
    data = Mutual.objects.all()
    return render(request, 'tu_vista.html', {'data': data})

def obtener_mes_y_anio_actual():
        # Encontrar la zona horaria basada en la ubicación
        tz_finder = TimezoneFinder()
        ubicacion = tz_finder.timezone_at(lng=-64.1428, lat=-31.4201)  # Coordenadas de Buenos Aires

        # Obtener la fecha y hora actual en la zona horaria de Buenos Aires
        zona_horaria_argentina = pytz.timezone(ubicacion)
        fecha_hora_actual = datetime.today()

        # Obtener el mes y el año actual de forma dinámica en español
        mes_actual = fecha_hora_actual.month
        año_actual = fecha_hora_actual.year
        
        print(año_actual)
        
        periodo = datetime(año_actual, mes_actual, 1).date()
       
        print(periodo)
        # Devolver el mes y el año en un solo string
        return periodo

def es_numerico(cadena):
        """Verifica si una cadena está compuesta solo por dígitos."""
        return bool(re.match("^\d+$", cadena))

def validar_numero(self, line_content, line_number, inicio, fin, tipo_numero):
        """Valida un número en una línea."""
        numero = line_content[inicio:fin]
        mensaje = f"{tipo_numero}: {numero}"
        print(mensaje)

        if not es_numerico(numero):
            mensaje_error = f"Error: La línea {line_number}. {mensaje} tiene caracteres no numéricos. Línea: {line_content}"
            messages.warning(self.request, mensaje_error)


def obtenerMutualVinculada(self):
    userRol = UserRol.objects.get(user=self.request.user)
    mutual = userRol.rol.cliente.mutual
    return mutual

def obtenerPeriodoVigente(self):
  try:
        periodoActual = obtener_mes_y_anio_actual()
        mutual = obtenerMutualVinculada(self)
        if(DeclaracionJurada.objects.get(periodo = periodoActual, mutual = mutual)):
                dj = DeclaracionJurada.objects.get(periodo = periodoActual)
                if(dj.leida):
                    mesSiguiente = periodoActual + relativedelta(months=1)
                    print(mesSiguiente)
                    return mesSiguiente
                else:
                    return periodoActual
        
  except ObjectDoesNotExist: 
         return periodoActual

  return periodoActual
       
          
    # # DeclaracionJurada.objects.get()
    # return  obtener_mes_y_anio_actual()

class DeclaracionJuradaView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    permission_required = 'mutual.add_declaracionjurada'
    model = DetalleDeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Declaración Jurada'

        mutual = obtenerMutualVinculada(self)
        periodo = obtenerPeriodoVigente(self)
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        periodoText = calendar.month_name[periodo.month].upper() + " " + str(periodo.year)
        context['periodo'] =  periodoText

        # Obtener la mutual actual
        context['mutual'] = mutual.nombre

        return context

    def form_valid(self, form):
        mutual = obtenerMutualVinculada(self)
        archivoPrestamo = form.cleaned_data['archivo_p']
        archivoReclamo = form.cleaned_data['archivo_r']
        try:
                with transaction.atomic():
                    archivo_valido_p = self.validar_prestamo(form, archivoPrestamo)
                    archivo_valido_r =  self.validar_reclamo(form, archivoReclamo)
                    print("ARCHIVO PRESTAMO VALIDO -->:", archivo_valido_p)
                    print("ARCHIVO RECLAMO VALIDO -->:", archivo_valido_r)
                    return super().form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error al procesar el formulario: {e}")
            return self.form_invalid(form)
        # try:
        #     with transaction.atomic():
                # archivo_valido_p = self.validar_prestamo(form, archivoPrestamo)
        #         archivo_valido_r = self.validar_reclamo(form, archivoReclamo)
                # print("ARCHIVO PRESTAMO VALIDO -->:", archivo_valido_p)
        #         print("ARCHIVO RECLAMO VALIDO -->:", archivo_valido_r)
        #         archivo_valido_p = False
        #         archivo_valido_r = False
        #         if archivo_valido_p:
        #             form.instance.periodo = obtener_mes_y_anio_actual()
        #             # Establecer la fecha de subida
        #             form.instance.fecha_subida = date.today()
        #             form.instance.mutual = obtenerMutualVinculada(self)
        #             form.instance.archivo = form.cleaned_data['archivos']
        #             form.instance.tipo = DeclaracionJurada.TIPO_DECLARACION[1][0]  # Asigna 'P' a tipo
        #             mensaje_error = "Prestamo cargado correctamente"

        #             mutual = get_object_or_404(Mutual, nombre=obtenerMutualVinculada(self).nombre)
        #             print(mutual)

        #             prestamo_en_periodo = DeclaracionJurada.objects.filter(mutual=mutual, tipo='P', periodo=obtener_mes_y_anio_actual()).first()
        #             print(prestamo_en_periodo)
        #             # Eliminar el objeto prestamo_en_periodo de la base de datos
        #             if prestamo_en_periodo:
        #                 prestamo_en_periodo.delete()

        #             messages.success(self.request, mensaje_error)
        #             return super().form_valid(form)                    
        #         else:
                    #  print("es invalido")
                    #  return super().form_invalid(form)
       

    def form_invalid(self, form):
        print("complete la carga de archivos")
        
        for field, errors in form.errors.items():
            print(f"Error en el campo {field}: {', '.join(errors)}")

        messages.error(self.request, 'Error en el formulario. Por favor, corrige los errores marcados.')
        return super().form_invalid(form)

    def validar_prestamo(self, form, archivo):
        """Valida el contenido del archivo de PRESTAMO."""
        print("VALIDANDO PRESTAMO------------")
        print("")
        todas_las_lineas_validas = True  # Variable para rastrear si todas las líneas son válidas
        LONGITUD_P = 54

        try:
                file = archivo.open() 
                for line_number, line_content_bytes in enumerate(file, start=1):
                    line_content = line_content_bytes.decode('utf-8').rstrip('\r\n')
                    print(f"Línea {line_number}: {line_content}")
                    
                    # Verificar la longitud de la línea incluyendo espacios en blanco y caracteres de nueva línea
                    if len(line_content) != LONGITUD_P:
                        todas_las_lineas_validas = False
                        break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                    else:
                        validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO")
                        validar_numero(self, line_content, line_number, 16, 20, "CONCEPTO")
                        validar_numero(self, line_content, line_number, 20, 31, "IMPORTE")
                        self.validar_fecha_prestamo(line_content, line_number, 31, 39, "FECHA INICIO")
                        self.validar_fecha_prestamo(line_content, line_number, 39, 47, "FECHA FIN")
                        validar_numero(self, line_content, line_number, 47, 54, "CUPON")
                    print("")
            
                if not todas_las_lineas_validas:
                    print("------------ PRESTAMO INVALIDO")
                    mensaje_error = f"Error: Todas las líneas del archivo deben tener {LONGITUD_P} caracteres."
                    messages.warning(self.request, mensaje_error)
                    return False
                print("------------ PRESTAMO VALIDO")
                return True

        except Exception as e:
                    messages.error(self.request, f"Error al leer el archivo: {e}")
                    return False

    def validar_fecha_prestamo(self, line_content, line_number, inicio, fin, tipo_fecha):
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

    def validar_reclamo(self, form, archivo):
        """Valida el contenido del archivo de RECLAMO."""
        print("VALIDANDO RECLAMO------------")
        print("")
        todas_las_lineas_validas = True  # Variable para rastrear si todas las líneas son válidas
        LONGITUD_R = 58
        try:
            file = archivo.open()
            for line_number, line_content_bytes in enumerate(file, start=1):
                line_content = line_content_bytes.decode('utf-8').rstrip('\r\n')
                print(f"Línea {line_number}: {line_content}")
                print(len(line_content))
                # Verificar la longitud de la línea incluyendo espacios en blanco y caracteres de nueva línea
                if len(line_content) != LONGITUD_R:
                    print("ESTOY EN EL IF")
                    todas_las_lineas_validas = False
                    break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                else:
                    validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO")
                    validar_numero(self, line_content, line_number, 16, 20, "CONCEPTO")
                    validar_numero(self, line_content, line_number, 20, 31, "IMPORTE")
                    self.validar_fecha_reclamo(line_content, line_number, 31, 39, "FECHA INICIO")
                    self.validar_fecha_reclamo:(line_content, line_number, 39, 47, "FECHA FIN")
                    validar_numero(self, line_content, line_number, 47, 54, "CUPON")
                    validar_numero(self,line_content, line_number, 54, 57, "CUOTA")
                print("")

            #   Después de procesar todas las líneas, mostrar el mensaje correspondiente
            if not todas_las_lineas_validas:
                print("RECLAMO INVALIDO------------")
                mensaje_error = f"Error: Todas las líneas del archivo deben tener {LONGITUD_R} caracteres."
                messages.warning(self.request, mensaje_error)
                return False
            print("RECLAMO VALIDO------------")
            return True

        except Exception as e:
          messages.error(self.request, f"Error al leer el archivo: {e}")
          return False

    def validar_fecha_reclamo(self, line_content, line_number, inicio, fin, tipo_fecha):
        fecha_str = line_content[inicio:fin]
        mensaje = f"{tipo_fecha}: {fecha_str}"
        print(mensaje)

        try:
            # Convertir la cadena de fecha a un objeto de fecha
            fecha_obj = datetime.strptime(fecha_str, "%d%m%Y").date()
            print(fecha_obj)

            # Obtener la fecha actual
            fecha_actual = date.today()

            # Comparar si la fecha de la línea está después de la fecha actual
            if fecha_obj > fecha_actual:
                mensaje_error = f"Error: La {tipo_fecha} en la línea {line_number} es posterior a la fecha actual. Línea: {line_content}"
                messages.warning(self.request, mensaje_error)

        except ValueError:
            mensaje_error = f"Error: La {tipo_fecha.lower()} en la línea {line_number} no es válida. Línea: {line_content}"
            messages.warning(self.request, mensaje_error)


        
<<<<<<< HEAD
=======
class DeclaracionJuradaReclamo(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = '/login/'  # Puedes personalizar la URL de inicio de sesión
    # permission_required = 'nombre_app.puede_realizar_accion'
    permission_required = 'mutual.add_declaracionjurada'
    model = DeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"
    LONGITUD = 57
    

    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Declaración Jurada (Reclamo)'
        context['mutual'] = obtenerMutualVinculada(self).nombre
        periodo = obtener_mes_y_anio_actual()
        context['periodo'] = obtenerPeriodoVigente(self)

        #[FALTA IMPLEMENTAR]
        # Verificar si la mutual ya ha cargado algún préstamo
        mutual = get_object_or_404(Mutual, nombre=context['mutual'])

        existe_reclamo_leido = DeclaracionJurada.objects.filter(mutual=mutual, tipo='R', periodo=periodo, leida=True).exists()
        print(existe_reclamo_leido)

        context['existe_reclamo_leido'] = False
        return context

    def form_valid(self, form):
        archivo = form.cleaned_data['archivos']

        try:
            with transaction.atomic():
                archivo_valido = self.validar_reclamo(form, archivo)

                if archivo_valido:
                    form.instance.periodo = obtener_mes_y_anio_actual()
                    # Establecer la fecha de subida
                    form.instance.fecha_subida = date.today()
                    form.instance.mutual = Mutual.objects.first()
                    form.instance.archivo = form.cleaned_data['archivos']
                    form.instance.tipo = DeclaracionJurada.TIPO_DECLARACION[0][0]  # Asigna 'R' a tipo (reclamo)
                    mensaje_error = "Reclamo cargado correctamente"
                    messages.success(self.request, mensaje_error)
                    return super().form_valid(form)                    
                else:
                     print("es invalido")
                     return super().form_invalid(form)

        except Exception as e:
            messages.error(self.request, f"Error al procesar el formulario: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Formulario no válido. Corrige los errores marcados.")
        
        for field, errors in form.errors.items():
            print(f"Error en el campo {field}: {', '.join(errors)}")

        messages.error(self.request, 'Error en el formulario. Por favor, corrige los errores marcados.')
        return super().form_invalid(form)
    
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
                if len(line_content) != self.LONGITUD:
                    print("ATRAPADAAAAAA")
                    todas_las_lineas_validas = False
                    break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                else:
                    validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO")
                    validar_numero(self, line_content, line_number, 16, 20, "CONCEPTO")
                    validar_numero(self, line_content, line_number, 20, 31, "IMPORTE")
                    self.validar_fecha_reclamo(line_content, line_number, 31, 39, "FECHA INICIO")
                    self.validar_fecha_reclamo:(line_content, line_number, 39, 47, "FECHA FIN")
                    validar_numero(self, line_content, line_number, 47, 54, "CUPON")
                    validar_numero(self,line_content, line_number, 54, 57, "CUOTA")
                print("")

            #   Después de procesar todas las líneas, mostrar el mensaje correspondiente
            if not todas_las_lineas_validas:
                mensaje_error = f"Error: Todas las líneas del archivo deben tener {self.LONGITUD} caracteres."
                messages.warning(self.request, mensaje_error)
                return False
            return True

        except Exception as e:
          messages.error(self.request, f"Error al leer el archivo: {e}")
          return False

    def validar_fecha_reclamo(self, line_content, line_number, inicio, fin, tipo_fecha):
        fecha_str = line_content[inicio:fin]
        mensaje = f"{tipo_fecha}: {fecha_str}"
        print(mensaje)

        try:
            # Convertir la cadena de fecha a un objeto de fecha
            fecha_obj = datetime.strptime(fecha_str, "%d%m%Y").date()
            print(fecha_obj)

            # Obtener la fecha actual
            fecha_actual = date.today()

            # Comparar si la fecha de la línea está después de la fecha actual
            if fecha_obj > fecha_actual:
                mensaje_error = f"Error: La {tipo_fecha} en la línea {line_number} es posterior a la fecha actual. Línea: {line_content}"
                messages.warning(self.request, mensaje_error)

        except ValueError:
            mensaje_error = f"Error: La {tipo_fecha.lower()} en la línea {line_number} no es válida. Línea: {line_content}"
            messages.warning(self.request, mensaje_error)

>>>>>>> 6d3aa72519d5a799bb8f2fbf7a6eb79dc748cfea

class DetalleMutualView(DetailView):
    model = Mutual
    template_name = 'detalle_mutual.html'
    context_object_name = 'mimutual'
    
    def get_object(self, queryset=None):  
      userRol = UserRol.objects.get(user = self.request.user )
      id = userRol.rol.cliente.mutual.id
      return Mutual.objects.get(id = id)
        
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