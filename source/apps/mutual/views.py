from typing import Any
from django.shortcuts import render, redirect
from django.views.generic import CreateView , TemplateView , DetailView
from .models import Mutual , DeclaracionJurada, Periodo
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..users.models import UserRol
import re
import locale
from datetime import datetime
import calendar
from timezonefinder import TimezoneFinder
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
        # zona_horaria_argentina = pytz.timezone(ubicacion)
        # print("zonee")
        # print( datetime.now(zona_horaria_argentina).date())
        
        # print("zonee")
        fecha_hora_actual = datetime.today()

        # Obtener el mes y el año actual de forma dinámica en español
        mes_actual = fecha_hora_actual.month
        año_actual = fecha_hora_actual.year
        
        # print(año_actual)
        
        periodo = datetime(año_actual, mes_actual, 1).date()
       
        # print(periodo)
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

#------------------------ VALIDACIÓN PARA EL CONCEPTO ------------------------
def validar_concepto(self, line_content, line_number, inicio, fin, tipo_numero, tipo_archivo):

    validar_numero(self, line_content, line_number, inicio, fin, tipo_numero)
    concepto = int(line_content[inicio:fin])

    if not existeConcepto(self, concepto, tipo_archivo):
        numero = line_content[inicio:fin]
        mensaje = f"{tipo_numero}: {numero}"
        print(mensaje, "NO ENCONTRADO EN BASE")
        mensaje_error = f"Error: La línea {line_number}. {mensaje} no esta vinculado a su mutual. Linea: {line_content}"
        messages.warning(self.request, mensaje_error)

#------------------------ VALIDACIÓN PARA EL IMPORTE ------------------------
def validar_importe(self, line_content, line_number, inicio, fin, tipo_numero, total_importe):
    validar_numero(self, line_content, line_number, inicio, fin, tipo_numero)
    importe_str = line_content[inicio:fin].lstrip('0')  # Remove leading zeros
    if not importe_str:
        importe_str = '0'
    importe_formatted = float(importe_str) /100 
    print("IMPORTE CONVERTIDO: ", importe_formatted)
    total_importe += importe_formatted  # Sumar el importe al total_importe
    print("TOTAL IMPORTE ACUMULADO: ", total_importe)

#--------------- VALIDA LA EXISTENCIA DEL CONCEPTO ------------------------
def existeConcepto(self, concepto, tipo_archivo):
    mutual = obtenerMutualVinculada(self)

    if mutual and mutual.detalle.exists():
        detalle_mutual = mutual.detalle.filter(tipo=tipo_archivo).first()
        if concepto == detalle_mutual.concepto_1 or concepto == detalle_mutual.concepto_2:
            return True
    return False

def obtenerMutualVinculada(self):
    userRol = UserRol.objects.get(user=self.request.user)
    mutual = userRol.rol.cliente.mutual
    return mutual

def obtenerPeriodoVigente(self):
  try:
        periodo = Periodo.objects.get(fecha_fin = None)
        # print(periodo)
        return periodo
        
  except Periodo.DoesNotExist: 
         return None
    # # DeclaracionJurada.objects.get()
    # return  obtener_mes_y_anio_actual()
#-----------------CONFIRMACION DJ---------------------------
class ConfirmacionView(TemplateView):
    template_name = 'confirmacion.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mutual = obtenerMutualVinculada(self)
        dj = DeclaracionJurada.objects.get(mutual = mutual )
        
        context['detalle_reclamao'] = dj.detalles.get(tipo = 'R')
        context['detalle_prestamo'] = dj.detalles.get(tipo = 'P')
        return context
    
    def post(self, request, *args, **kwargs):
        declaracion_borrador = DeclaracionJurada.objects.get(request.session.get('declaracion_borrador').id)
        declaracion_borrador.es_borrador = False






#--------------- DECLARACIÓN JURADA ------------------------
class DeclaracionJuradaView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    permission_required = 'mutual.add_declaracionjurada'
    model = DetalleDeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"
    success_url = '/confirmacion/'

    def get_success_url(self):
        return reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Declaración Jurada'

        mutual = obtenerMutualVinculada(self)
        periodoActual = obtenerPeriodoVigente(self)
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        context['periodo'] =  ""
        
        if(periodoActual != None):
            periodoText = calendar.month_name[periodoActual.mes_anio.month].upper() + " " + str(periodoActual.mes_anio.year)
            context['periodo'] =  periodoText

        # Obtener la mutual actual
        context['mutual'] = mutual.nombre

        try:
         borrador = DeclaracionJurada.objects.get(periodo = periodoActual , es_borrador = True, mutual = mutual)
         context['borrador'] = borrador
        except DeclaracionJurada.DoesNotExist:
            context['borrador'] = ""
        return context

    def form_valid(self, form):
        mutual = obtenerMutualVinculada(self)
        archivoPrestamo = form.cleaned_data['archivo_p']
        archivoReclamo = form.cleaned_data['archivo_r']
        
        try:
            with transaction.atomic():
                # archivo_valido_p = self.validar_prestamo(form, archivoPrestamo)
                # archivo_valido_r =  self.validar_reclamo(form, archivoReclamo)
                archivo_valido_r = True
                archivo_valido_p = True

                print("")
                print("ARCHIVO PRESTAMO VALIDO ->:", archivo_valido_p)
                print("ARCHIVO RECLAMO VALIDO -->:", archivo_valido_r)
                form.importe = 0

                if (archivo_valido_p and archivo_valido_r):
                    print("los dos archivos son correctos")
                    # Crear un objeto DetalleDeclaracionJurada con los valores adecuados
                    detalle_declaracion = form.save(commit=False)
                    detalle_declaracion.importe = 0  # Asignar el valor deseado al importe
                    detalle_declaracion.save()  # Guardar el objeto en la base de datos

                    print ("los dos archivos son correctos")
                    # --guardar como borrador + detalles
                    
                    return super().form_valid(form)
                return super().form_invalid(form)

        except Exception as e:
            messages.error(self.request, f"Error al procesar el formulario: {e}")
            return self.form_invalid(form)

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
        TIPO_ARCHIVO = 'P'
        total_importe = 0  # Inicializar el total del importe

        try:
                file = archivo.open() 
                for line_number, line_content_bytes in enumerate(file, start=1):
                    line_content = line_content_bytes.decode('utf-8').rstrip('\r\n')
                    print(f"Línea {line_number}: {line_content}")
                    
                    # Verificar la longitud de la línea incluyendo espacios en blanco y caracteres de nueva línea
                    if len(line_content) != LONGITUD_P:
                        print("REVISAR LINEA: ", line_number )
                        todas_las_lineas_validas = False
                        break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                    else:
                        validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO")
                        validar_concepto(self, line_content, line_number, 16, 20, "CONCEPTO", TIPO_ARCHIVO)
                        total_importe = validar_importe(self, line_content, line_number, 20, 31, "IMPORTE", total_importe)
                        
                        fecha_str_inicio = line_content[31:39]
                        fecha_str_fin = line_content[39:47]

                        self.validar_fechas_prestamo(line_content, line_number, fecha_str_inicio, fecha_str_fin)

                        validar_numero(self, line_content, line_number, 47, 54, "CUPON")
                    print("")
            
                if not todas_las_lineas_validas:
                    print("------------ PRESTAMO INVALIDO")
                    mensaje_error = f"Error: Todas las líneas del archivo deben tener {LONGITUD_P} caracteres."
                    messages.warning(self.request, mensaje_error)
                    return False, 0  # Devolver False y total_importes como 0 si hay líneas inválidas
                print("------------ PRESTAMO VALIDO")
                return True, total_importe

        except Exception as e:
                    messages.error(self.request, f"Error al leer el archivo: {e}")
                    return False


    def validar_fechas_prestamo(self, line_content, line_number, fecha_inicio, fecha_fin):

        try:
            # Convertir la cadena de fecha a un objeto de fecha
            print("FECHA INICIO: ", fecha_inicio)
            fecha_obj_inicio = datetime.strptime(fecha_inicio, "%d%m%Y").date()
            print("Fecha INICIO CONVERTIDA: ",fecha_obj_inicio)

            print("FECHA FIN: ", fecha_fin)
            fecha_obj_fin = datetime.strptime(fecha_fin, "%d%m%Y").date()
            print("Fecha FIN CONVERTIDA: ",fecha_obj_fin)
            
            periodoActual = obtenerPeriodoVigente(self)
            print(periodoActual.mes_anio)

            if fecha_obj_inicio > periodoActual.mes_anio:
                mensaje_error = f"Error: La FECHA INICIO en la línea {line_number} es mayor que la fecha inicial del periodo. Línea: {line_content}"

            if fecha_obj_fin < periodoActual.mes_anio:
                mensaje_error = f"Error: La FECHA FIN en la línea {line_number} es menor mayor que la fecha inicial del periodo. Línea: {line_content}"

            if fecha_obj_inicio > fecha_obj_fin:
                mensaje_error = f"Error: La FECHA INICIO en la línea {line_number} es mayor que la FECHA FIN. Línea: {line_content}"

        except ValueError:
            mensaje_error = f"Error: La FECHA en la línea {line_number} no es válida. Línea: {line_content}"
            messages.warning(self.request, mensaje_error)

    def validar_reclamo(self, form, archivo):
        """Valida el contenido del archivo de RECLAMO."""
        print("VALIDANDO RECLAMO------------")
        print("")
        todas_las_lineas_validas = True  # Variable para rastrear si todas las líneas son válidas
        LONGITUD_R = 57
        try:
            file = archivo.open()
            for line_number, line_content_bytes in enumerate(file, start=1):
                line_content = line_content_bytes.decode('utf-8').rstrip('\r\n')
                print(f"Línea {line_number}: {line_content}")
                print(len(line_content))
                # Verificar la longitud de la línea incluyendo espacios en blanco y caracteres de nueva línea
                if len(line_content) != LONGITUD_R:
                    todas_las_lineas_validas = False
                    break  # Salir del bucle tan pronto como encuentres una línea con longitud incorrecta
                else:
                    validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO")

                    validar_numero(self, line_content, line_number, 16, 20, "CONCEPTO")
                    
                    validar_numero(self, line_content, line_number, 20, 31, "IMPORTE")
                    self.validar_fecha_reclamo(line_content, line_number, 31, 39, "FECHA INICIO")
                    self.validar_fecha_reclamo:(line_content, line_number, 39, 47, "FECHA FIN") # type: ignore
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


    # def post(self, request, *args, **kwargs):
    #     self.object = None
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     archivoPrestamo = form.cleaned_data['archivo_p']
    #     archivoReclamo = form.cleaned_data['archivo_r']    
    #     archivo_valido_p = self.validar_prestamo(form, archivoPrestamo)
    #     archivo_valido_r =  self.validar_reclamo(form, archivoReclamo)
         
    #     if (archivo_valido_p & archivo_valido_r):
    #         #se crea el borrador 
    #         dj = DeclaracionJurada(mutual = obtenerMutualVinculada(self))
    #         dj.save()
    #         #se calculo los totales
    #         d_prestamo = DetalleDeclaracionJurada(tipo = 'P', archivo = archivo_valido_p , importe = 10000)
    #         d_reclamo  =DetalleDeclaracionJurada(tipo = 'R', archivo = archivoReclamo, importe = 1000)
    #         dj.detalles.create(d_prestamo)
    #         dj.detalles.create(d_reclamo)
    #         return render(request, 'mostrar_borrador.html',{'dj': dj} )
        
    #     render(request, self.template_name, {'form': form})

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