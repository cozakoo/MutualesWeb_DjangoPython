from io import BytesIO
import os
from tkinter import Canvas
from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView , TemplateView , DetailView
from .models import DeclaracionJuradaDetalles, Mutual , DeclaracionJurada, Periodo
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
from django.views.generic import ListView



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

#------------------------ OINTENGO EL TOTAL DEL IMPORTE ------------------------
def obtenerImporte(self, line_content, inicio, fin):
    importe_str = line_content[inicio:fin].lstrip('0')  # Remove leading zeros
    if not importe_str:
        importe_str = '0'
    importe_formatted = float(importe_str) /100 
    print("IMPORTE CONVERTIDO: ", importe_formatted)
    return importe_formatted

#--------------- VALIDA LA EXISTENCIA DEL CONCEPTO ------------------------
def existeConcepto(self, concepto, tipo_archivo):
    mutual = obtenerMutualVinculada(self)
    print(mutual.detalle.exists())
    if mutual and mutual.detalle.exists():
        detalle_mutual = mutual.detalle.filter(tipo=tipo_archivo).first()
        print(detalle_mutual)
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
         print("devuelvo none")
         return None
    # # DeclaracionJurada.objects.get()
    # return  obtener_mes_y_anio_actual()
#-----------------CONFIRMACION DJ---------------------------
class ConfirmacionView(TemplateView):
    template_name = 'confirmacion.html'
    success_url = '/confirmacion/'
    
    
    def get(self, request, *args, **kwargs):
        if request.GET.dict():
            super.get(self)
        else:
         return redirect('dashboard')
       
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mutual = obtenerMutualVinculada(self)
        # try:
        dj = DeclaracionJurada.objects.get(mutual = mutual, es_borrador = True )
        # except DeclaracionJurada.DoesNotExist:
        #  return context 
        context['mutual'] = mutual
        context['dj'] = dj
        context['detalle_reclamo'] = dj.detalles.get(tipo = 'R')
        context['detalle_prestamo'] = dj.detalles.get(tipo = 'P')
        return context

# ---------------------------------------------------------

class VisualizarErroresView(TemplateView):
    template_name = 'visualizar_errores.html'
    success_url = '/visualizarE/'

#--------------- DECLARACIÓN JURADA ------------------------
class DeclaracionJuradaView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    permission_required = 'mutual.add_declaracionjurada'
    model = DetalleDeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"
    success_url = '/confirmacion/'
        
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        
        
        if 'confirmacion' in request.POST:
           try:
                mutual = obtenerMutualVinculada(self)
                dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = True)
                dj.es_borrador = False
                dj.save()
                messages.success(self.request, "Declaracion Jurada confirmada")
                return redirect('dashboard')

           except DeclaracionJurada.DoesNotExist:
               return redirect('dashboard')
               
            #    mensaje informndo que lo que se quiere confirmar no esta disponible
            
      
                
        if 'cancelar' in request.POST:
            try:
                mutual = obtenerMutualVinculada(self)
                dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = True)
                dj.detalles.all().delete()
                dj.delete()
                print("borrado")

                messages.success(self.request, "Declaracion Jurada se ha eliminado")
                # return HttpResponse("exito al eliminar declaracion")
                return redirect('dashboard')

            except DeclaracionJurada.DoesNotExist:
                return redirect('dashboard')
       
        form = self.get_form()
       
        if 'cargarDeclaracion' in request.POST: 
           # Obtén una instancia del formulario
          print("sin error 1")
          if form.is_valid():
            print("sin error 2")
            # Hacer algo si el formulario es válido
            return self.form_valid(form)
            
          else:
            # Hacer algo si el formulario no es válido
            print("sin error 3")
            return self.form_invalid(form)
         
        return super().post(request, *args, **kwargs)
        
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
         dj = DeclaracionJurada.objects.get(mutual = obtenerMutualVinculada(self), es_borrador = True )
         contexto = {'dj': dj,
                     'd_prestamo': dj.detalles.get(tipo = 'P'),
                     'd_reclamo': dj.detalles.get(tipo = 'R')
                     
                     }
                    
         return render(request, 'confirmacion.html', contexto)
        except DeclaracionJurada.DoesNotExist:
          print("NO EXIST BORRADOR")
          return super().get(request, *args, **kwargs)
        
        
    def get_success_url(self):
        return reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Declaración Jurada'

        mutual = obtenerMutualVinculada(self)
        periodoActual = obtenerPeriodoVigente(self)
        print("PERIODO ACTUAAAL")
        print(periodoActual)
        # locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        context['periodoActual'] = periodoActual
        context['periodo'] =  ""
        
        if(periodoActual != None):
            # periodoText = calendar.month_name[periodoActual.mes_anio.month].upper() + " " + str(periodoActual.mes_anio.year)
            context['periodo'] =  "nuevo periodo"

        # Obtener la mutual actual
        context['mutual'] = mutual.nombre

        return context

    def form_valid(self, form):
        
        print("entre al valid sin errores")
        mutual = obtenerMutualVinculada(self)
        print("despues obt mutual ")
        periodoActual = obtenerPeriodoVigente(self)
        archivoPrestamo = form.cleaned_data['archivo_p']
        archivoReclamo = form.cleaned_data['archivo_r']
        print("antes del try")
        try:
            with transaction.atomic():
                archivo_valido_p, importe_p, total_registros_p = self.validar_prestamo(form, archivoPrestamo)
                archivo_valido_r, importe_r, total_registros_r = self.validar_reclamo(form, archivoReclamo)

                print("")
                print("ARCHIVO PRESTAMO VALIDO ->:", archivo_valido_p)
                print("ARCHIVO RECLAMO VALIDO -->:", archivo_valido_r)
                form.importe = 0

                if (archivo_valido_p and archivo_valido_r):
                    print("los dos archivos son correctos")
                    
                    declaracionJurada = DeclaracionJurada.objects.create(
                        mutual = mutual,
                        fecha_creacion = datetime.now(),
                        periodo = periodoActual
                    )

                    # Crear un objeto DetalleDeclaracionJurada con los valores adecuados
                    detalle_declaracion = form.save(commit=False)
                    detalle_declaracion.importe = importe_p
                    detalle_declaracion.tipo = 'P'
                    detalle_declaracion.archivo = archivoPrestamo
                    detalle_declaracion.total_registros = total_registros_p
                    detalle_declaracion.save()  # Guardar el objeto en la base de datos

                    # Crear objeto DetalleDeclaracionJurada para reclamo
                    detalle_reclamo = DetalleDeclaracionJurada.objects.create(
                        tipo='R',
                        importe=importe_r,
                        archivo=archivoReclamo,
                        total_registros=total_registros_r,
                    )

                    declaracionJuradaDetalle_r = DeclaracionJuradaDetalles.objects.create(
                        declaracionJurada = declaracionJurada,
                        detalleDeclaracionJurada = detalle_declaracion
                    )

                    declaracionJuradaDetalle_p = DeclaracionJuradaDetalles.objects.create(
                        declaracionJurada = declaracionJurada,
                        detalleDeclaracionJurada = detalle_reclamo
                    )

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
        last_line_number = 0  # Variable para almacenar el último line_number

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
                        validar_numero(self, line_content, line_number, 20, 31, "IMPORTE")
                        total_importe += obtenerImporte(self, line_content, 20, 31)
                        fecha_str_inicio = line_content[31:39]
                        fecha_str_fin = line_content[39:47]
                        self.validar_fechas_prestamo(line_content, line_number, fecha_str_inicio, fecha_str_fin)
                        validar_numero(self, line_content, line_number, 47, 54, "CUPON")
                        last_line_number = line_number  # Actualizar el último line_number
                    print("")
            
                if not todas_las_lineas_validas:
                    print("------------ PRESTAMO INVALIDO")
                    mensaje_error = f"Error: Todas las líneas del archivo deben tener {LONGITUD_P} caracteres."
                    messages.warning(self.request, mensaje_error)
                    return False, 0, last_line_number  # Devolver False y total_importes como 0 si hay líneas inválidas
                print("------------ PRESTAMO VALIDO")
                return True, total_importe, last_line_number

        except Exception as e:
            messages.error(self.request, f"Error al leer el archivo: {e}")
            return False, 0, last_line_number


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
        total_importe = 0  # Inicializar el total del importe
        last_line_number = 0  # Variable para almacenar el último line_number

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
                    total_importe += obtenerImporte(self, line_content, 20, 31)
                    self.validar_fecha_reclamo(line_content, line_number, 31, 39, "FECHA INICIO")
                    self.validar_fecha_reclamo:(line_content, line_number, 39, 47, "FECHA FIN") # type: ignore
                    validar_numero(self, line_content, line_number, 47, 54, "CUPON")
                    validar_numero(self,line_content, line_number, 54, 57, "CUOTA")
                    last_line_number = line_number  # Actualizar el último line_number
                print("")

            #   Después de procesar todas las líneas, mostrar el mensaje correspondiente
            if not todas_las_lineas_validas:
                print("RECLAMO INVALIDO------------")
                mensaje_error = f"Error: Todas las líneas del archivo deben tener {LONGITUD_R} caracteres."
                messages.warning(self.request, mensaje_error)
                return False, 0, last_line_number
            print("RECLAMO VALIDO------------")
            return True, total_importe, last_line_number

        except Exception as e:
          messages.error(self.request, f"Error al leer el archivo: {e}")
          return False, 0, last_line_number

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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class HistoricoView(ListView):
    model = DeclaracionJurada
    template_name = "dj_list.html"
    paginate_by = 10# Número de elementos por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Historico'
        return context
    

def generate_pdf(declaracion):
    print(declaracion)
    # Crear el PDF en memoria
    pdf_bytes = BytesIO()
    pdf = Canvas.Canvas(pdf_bytes)

    # Agregar contenido al PDF (puedes personalizar esto según tus necesidades)
    pdf.drawString(100, 100, f"Contenido de la declaración jurada: {declaracion}")

    # Guardar el estado del PDF y cerrar el objeto PDF
    pdf.showPage()
    pdf.save()

    # Configurar la respuesta para devolver el PDF en lugar de guardarlo en un archivo
    pdf_bytes.seek(0)  # Asegúrate de que el cursor esté al principio del archivo

    # Guardar el PDF en un archivo temporal
    pdf_filename = os.path.join("/ruta/del/archivo/temporal", "declaracion_jurada.pdf")
    with open(pdf_filename, 'wb') as pdf_file:
        pdf_file.write(pdf_bytes.read())

    # Puedes devolver el nombre del archivo temporal si lo necesitas
    return pdf_filename


def descargarDeclaracion(request, pk):
    
    declaracion = get_object_or_404(DeclaracionJurada, pk=pk)
    generate_pdf(declaracion)
    return HttpResponse()
