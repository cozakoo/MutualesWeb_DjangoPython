from io import BytesIO
import io
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import CreateView , TemplateView , DetailView , UpdateView
from .models import DeclaracionJuradaDetalles, DetalleMutual, Mutual , DeclaracionJurada, Periodo
from .forms import *
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..users.models import UserRol
import re
import locale
from datetime import datetime
from timezonefinder import TimezoneFinder
from django.utils.translation import gettext as _
from datetime import date
from django.views.generic import ListView
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import permission_required, login_required
from django.http import JsonResponse
from django.db.models import Q




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

def validar_numero(self, line_content, line_number, inicio, fin, tipo_numero, listErrores):
        """Valida un número en una línea."""
        numero = line_content[inicio:fin]
        mensaje = f"{tipo_numero}: {numero}"
        print(mensaje)

        if not es_numerico(numero):
            listErrores.append(f"Error: La línea {line_number}. {mensaje} tiene caracteres no numéricos. Línea: {line_content}")
            # messages.warning(self.request, mensaje_error)

#------------------------ VALIDACIÓN PARA EL CONCEPTO ------------------------
def validar_concepto(self, line_content, line_number, inicio, fin, tipo_numero, tipo_archivo, listErrores):

    validar_numero(self, line_content, line_number, inicio, fin, tipo_numero, listErrores)
    concepto = int(line_content[inicio:fin])

    if not existeConcepto(self, concepto, tipo_archivo):
        numero = line_content[inicio:fin]
        mensaje = f"{tipo_numero}: {numero}"
        print(mensaje, "NO ENCONTRADO EN BASE")
        listErrores.append(f"Error: La línea {line_number}. {mensaje} no esta vinculado a su mutual. Linea: {line_content})")
     

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

from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime

def fecha_es_mayor_por_meses(fecha2):
    MESES = 2
    fecha1 = datetime.now()

    # Convierte fecha2 a un objeto datetime para la comparación
    fecha2_datetime = datetime.combine(fecha2, datetime.min.time())
    
    nueva_fecha = fecha2_datetime + relativedelta(months=MESES)
    
    # Compara la nueva fecha con la fecha1
    return nueva_fecha < fecha1
#-----------------CONFIRMACION DJ---------------------------
class ConfirmacionView(TemplateView):
    template_name = 'confirmacion.html'
    success_url = '/confirmacion/'
    
    
    def get(self, request, *args, **kwargs):
        if request.GET.dict():
            super.get(self)
        else:
         return redirect('dashboard')
       
        
    
#-----------------CONFIRMACION DJ---------------------------
class MsjInformativo(TemplateView):
    template_name = 'msj_informativo.html'
    success_url = '/msj_info/'
    
    
    def get(self, request, *args, **kwargs):
        if request.GET.dict():
            super.get(self)
        else:
         return redirect('dashboard')
       
        


def existeBorrador(self):
            try: 
                    mutual = obtenerMutualVinculada(self) 
                    dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = True)
                    return True

            except DeclaracionJurada.DoesNotExist:
                return False
    
            
# ---------------------------------------------------------

class VisualizarErroresView(TemplateView):
    template_name = 'visualizar_errores.html'
    success_url = '/visualizarE/'
    
    def get(self, request, *args, **kwargs):
        if request.GET.dict():
            super.get(self)
        else:
         return redirect('dashboard')

#--------------- DECLARACIÓN JURADA ------------------------
class DeclaracionJuradaCreateView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    permission_required = "clientes.permission_cliente_mutual"
    model = DetalleDeclaracionJurada
    form_class = FormularioDJ
    template_name = "dj_alta.html"
    success_url = reverse_lazy('mutual:declaracion_jurada', args=['accion=declarar'])

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if 'confirmacion' in request.POST:

           mutual = obtenerMutualVinculada(self)
           nroRectificativa = 0
           if existeBorrador(self) :
            try:
                periodo = obtenerPeriodoVigente(self)
                dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = False, periodo = periodo)
                nroRectificativa = dj.rectificativa + 1
                dj.detalles.all().delete()
                dj.delete()
            except DeclaracionJurada.DoesNotExist:
                print("omite")
            
            try:
                        
                        dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = True)
                        dj.es_borrador = False
                        dj.rectificativa = nroRectificativa
                        dj.fecha_subida = datetime.now()
                        dj.save()
                        messages.success(self.request, "Declaracion Jurada confirmada")
                        return redirect('mutual:historico')

            except DeclaracionJurada.DoesNotExist:
                    return redirect('dashboard')
           
           
           return redirect('dashboard')
               
        if 'cancelar' in request.POST:
            try:
                mutual = obtenerMutualVinculada(self)
                dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = True)
                dj.detalles.all().delete()
                dj.delete()
                print("borrado")

                messages.success(self.request, "EL Borrador de Declaracion jurada se ha eliminado")
                # return HttpResponse("exito al eliminar declaracion")
                return redirect('dashboard')

            except DeclaracionJurada.DoesNotExist:
                return redirect('dashboard')
       
        form = self.get_form()
       
        if 'cargarDeclaracion' in request.POST: 
           # Obtén una instancia del formulario
           
           try:
             DeclaracionJurada.objects.get(mutual = obtenerMutualVinculada(self), periodo = obtenerPeriodoVigente(self), es_borrador = True)
             return render(request, 'dj_alta.html')
           except DeclaracionJurada.DoesNotExist: 
                print("sin error 1")
                if form.is_valid():
                    print("sin error 2")
                    # Hacer algo si el formulario es válido
                    return self.form_valid(form)
                    
                else:
                    # Hacer algo si el formulario no es válido
                    print("sin error 3")
                    return self.form_valid(form)
        
         
        return super().post(request, *args, **kwargs)
        
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        
        periodo = obtenerPeriodoVigente(self)
        
        mutual = obtenerMutualVinculada(self)
        
        if(not mutual.activo):
            msj = ("El estado de su mutual está inactivo, por lo tanto, no puede realizar declaraciones juradas en este momento.")
            contexto = {'msj': msj}
            return render(request, 'msj_informativo.html', contexto)
            
        if periodo == None:
            print("redirijo msj")
            msj = ("No existe un Periodo de Declaración Jurada disponible actualmente.")
            contexto = {'msj': msj}
            return render(request, 'msj_informativo.html', contexto)
        
        
      
        
        try:
            dj = DeclaracionJurada.objects.get(mutual = obtenerMutualVinculada(self), es_borrador = False,  periodo = periodo , es_leida = True  )
            msj = ("Rectificación de declaración jurada no disponible. Última declaración ya fue leída.")
            print("aviso se va rectificar")
            contexto = {'msj': msj}
            return render(request, 'msj_informativo.html', contexto)
        except DeclaracionJurada.DoesNotExist:
            print("Se puede declarar o rectificar")
        
        
        
        contexto = {}
        try:
         dj = DeclaracionJurada.objects.get(mutual = obtenerMutualVinculada(self), es_borrador = True )
         contexto['dj'] = dj 
          
         try:
          contexto['d_prestamo'] = dj.detalles.get(tipo = 'P') 
         except DetalleDeclaracionJurada.DoesNotExist:
          print("no se agrega detalle 1")
          
         try:
          contexto['d_reclamo'] = dj.detalles.get(tipo = 'R') 
         except DetalleDeclaracionJurada.DoesNotExist:
          print("no se agrega detalle2")
                    
                    
         return render(request, 'confirmacion.html', contexto)
        except DeclaracionJurada.DoesNotExist:
          print("NO EXIST BORRADOR")
          
          return super().get(request, *args, **kwargs)
        
        
    # def get_success_url(self):
    #     return reverse_lazy('declaracion_jurada')




    def presentaDetalle(self , detalle:DetalleMutual):
        return detalle.origen != "*" and detalle.destino != "*" and detalle.concepto_1 > 1 
    

    
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accion = self.kwargs.get('accion')

        if accion == 'rectificar':
            context['titulo'] = 'Declaración Rectificativa'
        else:
            context['titulo'] = 'Declaración Jurada'
        
        mutual = obtenerMutualVinculada(self)
        periodoActual = obtenerPeriodoVigente(self)
        

        context['existe_prestamo'] = self.presentaDetalle(mutual.detalle.get(tipo='P'))
        context['existe_reclamo'] = self.presentaDetalle(mutual.detalle.get(tipo='R'))
        
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
        mutual = obtenerMutualVinculada(self)
        periodoActual = obtenerPeriodoVigente(self)
        listErroresPrestamo = []
        listErroresReclamo = []
        # archivoReclamo = False
        # archivoPrestamo = False 
        # try:
        #     archivoPrestamo = form.cleaned_data['archivo_p']
        # except KeyError:
        #     print("prestamo no se encontro", archivoPrestamo)
            
        # try:
        #     archivoReclamo = form.cleaned_data['archivo_r']
        # except KeyError:
        #     print("reclamo no se encontro", archivoReclamo) 
        archivoPrestamo = form.cleaned_data['archivo_p']
        archivoReclamo = form.cleaned_data['archivo_r']
        print("antes del try")
        
        try:
            with transaction.atomic():
                if archivoPrestamo: archivo_valido_p, importe_p, total_registros_p, listErroresPrestamo = self.validar_prestamo(form, archivoPrestamo)
                else: archivo_valido_p = True
                
                if archivoReclamo : archivo_valido_r, importe_r, total_registros_r, listErroresReclamo = self.validar_reclamo(form, archivoReclamo)
                else: archivo_valido_r = True
                
                
                
                print("estado archivos")
                print(archivoPrestamo,archivoReclamo)
                print("ARCHIVO PRESTAMO VALIDO ->:", archivo_valido_p)
                print("ARCHIVO RECLAMO VALIDO -->:", archivo_valido_r)
                form.importe = 0
                
                if (archivo_valido_p and archivo_valido_r):
                    print("los dos archivos son correctos")
                    
                    
                    declaracionJurada = DeclaracionJurada.objects.create(
                        mutual = mutual,
                        fecha_creacion = datetime.now(),
                        periodo = periodoActual,
                        es_borrador = True
                    )
                    
                    # Crear un objeto DetalleDeclaracionJurada con los valores adecuados
                    if archivoPrestamo:
                        print("entre creacion det prestamo")
                        detalle_Prestamo = declaracionJurada.detalles.create(
                            tipo='P',
                            importe=importe_p,
                            archivo=archivoPrestamo,
                            total_registros=total_registros_p,
                        )
                        
                    
                    if archivoReclamo:
                        print("entre creacion det reclamo")
                        print(listErroresReclamo)
                    # Crear objeto DetalleDeclaracionJurada para reclamo
                        detalle_reclamo = declaracionJurada.detalles.create(
                            tipo='R',
                            importe=importe_r,
                            archivo=archivoReclamo,
                            total_registros=total_registros_r,
                        )
                    
                    print("entre en valid")
                    return super().form_valid(form)
                
                print("entre en invalid")
                return self.form_invalid(form, listErroresPrestamo, listErroresReclamo)

        except Exception as e:
            print("exepcion is valid")
            messages.error(self.request, f"Error al procesar el formulario: {e}")
            return self.form_invalid(form,listErroresPrestamo,listErroresReclamo)


     
    def form_invalid(self, form, listErroresPrestamo, listErroresReclamo):
        
        contexto = {
            'mutual': obtenerMutualVinculada(self),
            'erroresPrestamo': listErroresPrestamo,
             'cantErrorPrestamo': len(listErroresPrestamo),
            'erroresReclamo':listErroresReclamo,
            'cantErrorReclamo': len(listErroresReclamo)
        }
        
       
        return render(self.request, 'visualizar_errores.html', contexto)
        # messages.error(self.request, 'Error en el formulario. Por favor, corrige los errores marcados.')
        

    def validar_prestamo(self, form, archivo):
        """Valida el contenido del archivo de PRESTAMO."""
        print("VALIDANDO PRESTAMO------------")
        print("")
        listErrores = []
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
                        validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO",listErrores)
                        validar_concepto(self, line_content, line_number, 16, 20, "CONCEPTO", TIPO_ARCHIVO, listErrores)
                        validar_numero(self, line_content, line_number, 20, 31, "IMPORTE", listErrores)
                        total_importe += obtenerImporte(self, line_content, 20, 31)
                        fecha_str_inicio = line_content[31:39]
                        fecha_str_fin = line_content[39:47]
                        self.validar_fechas_prestamo(line_content, line_number, fecha_str_inicio, fecha_str_fin,listErrores)
                        validar_numero(self, line_content, line_number, 47, 54, "CUPON", listErrores)
                        last_line_number = line_number  # Actualizar el último line_number
                    
                    print("")
            
                if not todas_las_lineas_validas:
                    print("------------ PRESTAMO INVALIDO")
                    listErrores.append(f"Error: Todas las líneas del archivo deben tener {LONGITUD_P} caracteres.")
                    # messages.warning(self.request, mensaje_error)
                    return False, 0, last_line_number, listErrores # Devolver False y total_importes como 0 si hay líneas inválidas
                print("------------ PRESTAMO VALIDO")
                
                if len(listErrores) != 0:
                    return False, total_importe, last_line_number, listErrores
                return True, total_importe, last_line_number, listErrores
             

        except Exception as e:
            listErrores.append(f"Archivo invalido no puede ser leido: {e}")
            return False, 0, last_line_number, listErrores

    
    
    def convertirFechaEntero(fecha:date):
        return fecha.year + fecha.day  
    
    
    def validar_fechas_prestamo(self, line_content, line_number, fecha_inicio, fecha_fin, listErrores):
        
        
        
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
         
            
            if fecha_obj_inicio.month > periodoActual.mes_anio.month and fecha_obj_inicio.year >= periodoActual.mes_anio.year :
                listErrores.append(f"Error: La FECHA INICIO en la línea {line_number} No corresponde al periodo a declarar. Línea: {line_content}")

            if fecha_obj_fin < periodoActual.mes_anio:
                listErrores.append(f"Error: La FECHA FIN en la línea {line_number} es menor mayor que la fecha inicial del periodo. Línea: {line_content}")

            if fecha_obj_inicio > fecha_obj_fin:
               listErrores.append(f"Error: La FECHA INICIO en la línea {line_number} es mayor que la FECHA FIN. Línea: {line_content}")
            
        
        except ValueError:
            mensaje_error = f"Error: La FECHA en la línea {line_number} no es válida. Línea: {line_content}"
            listErrores.append(mensaje_error)
            
      
    def validar_fechas_reclamo(self, line_content, line_number, fecha_inicio, fecha_fin, listErrores):
        
        
        
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
         
            
            if fecha_obj_inicio >= periodoActual.mes_anio:
                listErrores.append(f"Error: La FECHA INICIO en la línea {line_number} Fecha de inicio del reclamo no es válida. Debe ser anterior al período declarativo actual. Línea: {line_content}")

           

            if fecha_obj_inicio > fecha_obj_fin:
               listErrores.append(f"Error: La FECHA INICIO en la línea {line_number} es mayor que la FECHA FIN. Línea: {line_content}")
            
        
        except ValueError:
            mensaje_error = f"Error: La FECHA en la línea {line_number} no es válida. Línea: {line_content}"
            listErrores.append(mensaje_error)
            


    def validar_reclamo(self, form, archivo):
        """Valida el contenido del archivo de RECLAMO."""
        print("VALIDANDO RECLAMO------------")
        print("")
        TIPO_ARCHIVO = 'R'
        listErrores = []
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
                    validar_numero(self, line_content, line_number, 3, 16, "DOCUMENTO",listErrores)
                    validar_concepto(self, line_content, line_number, 16, 20, "CONCEPTO", TIPO_ARCHIVO, listErrores)
                    validar_numero(self, line_content, line_number, 20, 31, "IMPORTE",listErrores)
                    total_importe += obtenerImporte(self, line_content, 20, 31)
                    fecha_str_inicio = line_content[31:39]
                    fecha_str_fin = line_content[39:47]
                    self.validar_fechas_reclamo(line_content, line_number, fecha_str_inicio, fecha_str_fin,listErrores)
                    
                    
                    validar_numero(self, line_content, line_number, 47, 54, "CUPON", listErrores)
                    validar_numero(self,line_content, line_number, 54, 57, "CUOTA", listErrores)
                    last_line_number = line_number  # Actualizar el último line_number
                print("")

            #   Después de procesar todas las líneas, mostrar el mensaje correspondiente
            if not todas_las_lineas_validas:
                print("RECLAMO INVALIDO------------")
                listErrores.append(f"Error: Todas las líneas del archivo deben tener {LONGITUD_R} caracteres.")
                
                # messages.warning(self.request, mensaje_error)
                return False, 0, last_line_number, listErrores
            print("RECLAMO VALIDO------------")
            if len(listErrores) != 0:
                return False, total_importe, last_line_number, listErrores
            return True, total_importe, last_line_number, listErrores

        except Exception as e:
          listErrores.append(f"Archivo invalido no puede ser leido {e}")
          return False, 0, last_line_number



class DetalleMutualView(LoginRequiredMixin,PermissionRequiredMixin, DetailView):
    login_url = '/login/'
    model = Mutual
    template_name = 'detalle_mutual.html'
    context_object_name = 'mimutual'
    permission_required = "clientes.permission_cliente_mutual"
    
    def get_object(self, queryset=None):  
      userRol = UserRol.objects.get(user = self.request.user )
      id = userRol.rol.cliente.mutual.id
      return Mutual.objects.get(id = id)
        
        
        
        
class MutualUpdateView(UpdateView):
    model = Mutual
    fields = ['nombre', 'cuit' ,'activo']
    template_name = 'mutual_update_form.html'  
    success_url="/dashboard/"   
        
        
        
        
        
        
class MutualCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Mutual
    form_class = FormularioMutual
    template_name = 'mutual_alta.html'
    success_url = reverse_lazy('mutual:mutual_exito')
    login_url = "/login/"
    permission_required = "empleadospublicos.permission_empleado_publico"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not 'detalle_prestamo' in context:
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
                print("invalid")
                return self.form_invalid(form,detalle_prestamo, detalle_reclamo)
    
 
    def form_invalid(self, form, detalle_p, detalle_r):
        return self.render_to_response(self.get_context_data(form=form, detalle_prestamo = detalle_p, detalle_reclamo = detalle_r))
    
    def form_valid(self, form, d_reclamo, d_prestam):

            # Si no existe, guarda el objeto y realiza las acciones necesarias
            with transaction.atomic():    
                m = Mutual.objects.create(
                    nombre=form.cleaned_data["nombre"],
                    alias=form.cleaned_data["alias"],
                    cuit=form.cleaned_data["cuit"],
                    activo = True,
                )
                      
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
        
            # url = reverse('mutual_exito')
            # return HttpResponseRedirect(url)
            messages.success(self.request, 'Mutual creada con exito')
            return redirect('mutual:mutual_crear')
    
    
    
def mutual_exito(request):
    return render(request,'mutual_exito.html')
  
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['titulo'] = "Alta de cliente"
    #     return context

class HistoricoView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = '/login/'
    model = DeclaracionJurada
    template_name = "dj_list.html"
    paginate_by = 10# Número de elementos por página
    permission_required =  "clientes.permission_cliente_mutual"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Histórico'
        return context
    
    def get_queryset(self):
        # Filtrar los objetos según tu lógica
        mutual = obtenerMutualVinculada(self)
        queryset = DeclaracionJurada.objects.filter(es_borrador = False, mutual = mutual)

        # Devolver el queryset filtrado
        return queryset

def registrar_fuentes():
    pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
    pdfmetrics.registerFont(TTFont('TituloFont', 'times.ttf'))
    pdfmetrics.registerFont(TTFont('Times-Italic', 'timesi.ttf'))
    pdfmetrics.registerFont(TTFont('Times-Bold', 'timesbd.ttf'))

def establecer_fuente_titulo(pdf):
    pdf.setFont('Times-Bold', 14)
    pdf.drawCentredString(300, 770, "Presentación de DJ por internet")
    pdf.drawCentredString(300, 745, "Acuse de recibo de DJ")

def agregar_linea(pdf, y_position):
    pdf.setStrokeColorRGB(0.6, 0.6, 0.6)
    pdf.line(100, y_position, 520, y_position)
    pdf.setStrokeColorRGB(0, 0, 0)

def agregar_cabecera(pdf, mutual, periodo, codigo_acuse, fecha_subida, total_registros, suma_importes):
    agregar_linea(pdf, 715)
    pdf.setFont("Calibri", 11)
    pdf.drawRightString(295, 695, f'Mutual:')
    pdf.drawRightString(295, 675, f'CUIT:')
    pdf.drawRightString(295, 655, f'Fecha de Presentación:')
    pdf.drawRightString(295, 635, f'Código Acuse:')
    pdf.drawRightString(295, 615, f'Período:')    
    pdf.drawRightString(295, 595, f'Total de Importe:')
    pdf.drawRightString(295, 575, f'Total de Registros:')
    pdf.drawString(300, 695, f'{mutual.nombre}')
    pdf.drawString(300, 675, f'{mutual.cuit}')
    pdf.drawString(300, 655, f'{fecha_subida.strftime("%Y-%m-%d Hora: %H:%M:%S")}')
    pdf.drawString(300, 635, f'{codigo_acuse}')
    pdf.drawString(300, 615, f'{periodo.mes_anio.strftime("%Y - %m")}')
    pdf.drawString(300, 595, f'${suma_importes}')
    pdf.drawString(300, 575, f'{total_registros}')

def agregar_detalle(pdf, titulo, y_position, archivo, total_registros, importe):
    agregar_linea(pdf, y_position)
    pdf.setFont("Times-Italic", 11)
    pdf.drawCentredString(300, y_position - 20, titulo)
    pdf.setFont("Calibri", 11)
    pdf.drawRightString(295, y_position - 40, f'Archivo:')
    pdf.drawRightString(295, y_position - 60, f'Importe:')
    pdf.drawRightString(295, y_position - 80, f'Cantidad de Registros:')
    pdf.drawString(300, y_position - 40, f'{archivo}')
    pdf.drawString(300, y_position - 60, f'${importe}')
    pdf.drawString(300, y_position - 80, f'{total_registros}')

def agregar_pie_de_pagina(pdf):
    pdf.setFont("Calibri", 11)
    pdf.drawCentredString(300, 50, 'dgc.chubut@gmail.com')

def generate_pdf(declaracion):
    detalles_prestamo = declaracion.detalles.filter(tipo='P').first()
    detalles_reclamo = declaracion.detalles.filter(tipo='R').first()
    
    total_registros_prestamo = detalles_prestamo.total_registros if detalles_prestamo else 0
    total_registros_reclamo = detalles_reclamo.total_registros if detalles_reclamo else 0
    total_registros = total_registros_prestamo + total_registros_reclamo

    suma_importes_prestamo = detalles_prestamo.importe if detalles_prestamo else 0
    suma_importes_reclamo = detalles_reclamo.importe if detalles_reclamo else 0
    suma_importes = suma_importes_prestamo + suma_importes_reclamo

    registrar_fuentes()

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    locale.setlocale(locale.LC_TIME, 'es_ES.utf-8')

    establecer_fuente_titulo(pdf)
    agregar_cabecera(pdf, declaracion.mutual, declaracion.periodo, declaracion.codigo_acuse_recibo,
                    declaracion.fecha_subida, total_registros, suma_importes)

    if detalles_prestamo:
        nombre_archivo_prestamo = os.path.basename(detalles_prestamo.archivo.path) if detalles_prestamo else ""
        nombre_archivo_prestamo_sin_extension, extension_prestamo = os.path.splitext(nombre_archivo_prestamo)
        nombre_archivo_prestamo_sin_guion_bajo = nombre_archivo_prestamo_sin_extension.split('_')[0]
        nombre_final_prestamo = f"{nombre_archivo_prestamo_sin_guion_bajo}{extension_prestamo}"
        agregar_detalle(pdf, 'DETALLE PRÉSTAMO:', 545, nombre_final_prestamo, detalles_prestamo.total_registros, detalles_prestamo.importe)

    if detalles_reclamo:
        nombre_archivo_reclamo = os.path.basename(detalles_reclamo.archivo.path) if detalles_reclamo else ""
        nombre_archivo_reclamo_sin_extension, extension_reclamo = os.path.splitext(nombre_archivo_reclamo)
        nombre_archivo_reclamo_sin_guion_bajo = nombre_archivo_reclamo_sin_extension.split('_')[0]
        nombre_final_reclamo = f"{nombre_archivo_reclamo_sin_guion_bajo}{extension_reclamo}"
        agregar_detalle(pdf, 'DETALLE RECLAMO:', 435, nombre_final_reclamo, detalles_reclamo.total_registros, detalles_reclamo.importe)

    agregar_pie_de_pagina(pdf)
    locale.setlocale(locale.LC_TIME, '')

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer


@login_required(login_url="/login/")
def descargarDeclaracion(request, pk):
    print("entre descarga declara")
    declaracion = get_object_or_404(DeclaracionJurada, pk=pk)
    buffer = generate_pdf(declaracion)

    return FileResponse(buffer, as_attachment=True, filename="declaracion_jurada.pdf")





# def obtenerNombreDestino(self, tipo):
#     if tipo = "P"
#        m = obtenerMutualVinculada(self)
    
    
def descargarArchivo(request, pk):
    detalle = get_object_or_404(DetalleDeclaracionJurada, pk=pk)
    
    
    declaracion_jurada = get_object_or_404(DeclaracionJurada, detalles = detalle)
    
    mutual = declaracion_jurada.mutual
 
    detalleMutual = mutual.detalle.get(tipo = detalle.tipo)
    nombre = detalleMutual.destino + ".txt"

    # nombre = obtenerNombreDestino(request, detalle.tipo)
    with detalle.archivo.open('rb') as archivo:
        response = HttpResponse(archivo.read(), content_type='application/octet-stream')
        name = detalle.archivo.name.split("/")[-1]

        response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return response

from django.db.models import Q


class MutualesListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = "/login/"
    model = Mutual
    template_name = "mutuales_listado.html"
    paginate_by = 10  # Número de elementos por página
    permission_required = "empleadospublicos.permission_empleado_publico"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mutuales'
        context["mutuales"] = Mutual.objects.all().order_by('alias')
        context['filter_form'] = MutualFilterForm(self.request.GET)  # Agrega el formulario al contexto
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset().order_by('alias')
        filter_form = MutualFilterForm(self.request.GET)

        if filter_form.is_valid():
            concepto = filter_form.cleaned_data.get('concepto')
            estado = filter_form.cleaned_data.get('estado')
            cuit = filter_form.cleaned_data.get('cuit')
            print(concepto)

            if estado == '2':
                queryset = queryset.filter(activo=True)
            elif estado == '3':
                queryset = queryset.filter(activo=False)

            if cuit:
                queryset = queryset.filter(cuit=cuit)

            mutual_id = self.request.GET.get('enc_mutual')
            try:
                mutual_id = int(mutual_id)

                if mutual_id != 0: 
                    queryset = queryset.filter(pk=mutual_id)

            except (ValueError, TypeError):
                mutual_id = None

            finally:
                if concepto is not None:
                    print("ESTOY AQUI")
                    queryset = queryset.filter(
                    Q(detalle__concepto_1=concepto) | Q(detalle__concepto_2=concepto)
                    )
        return queryset

def obtenerPeriodosFinalizados():
    return Periodo.objects.filter(fecha_fin__isnull=False)

    
class DeclaracionJuradaDeclaradoListView(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    model = DeclaracionJurada
    template_name = "dj_declarados_list.html"
    paginate_by = 10  # Número de elementos por página
    login_url = "/login/"
    permission_required = "empleadospublicos.permission_empleado_publico"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Histórico'
        context['mutuales'] = Mutual.objects.all().order_by('alias')
        context['periodos'] = obtenerPeriodosFinalizados()
        context['filter_form'] = DeclaracionJuradaFilterForm(self.request.GET)

        return context

    def get_queryset(self):

        # Filtrar el queryset de DeclaracionJurada basado en los periodos sin fecha de fin
        queryset = DeclaracionJurada.objects.filter(periodo__in=obtenerPeriodosFinalizados())

        # Obtener los datos del formulario enviado por el usuario
        filter_form = DeclaracionJuradaFilterForm(self.request.GET)
        
        mutual_id = self.request.GET.get('enc_mutual')
        periodo_id = self.request.GET.get('enc_periodo')

        # Convertir mutual_id a entero si es posible
        try:
            mutual_id = int(mutual_id)
            periodo_id = int(periodo_id)

            if mutual_id != 0: 
                queryset = queryset.filter(mutual__pk=mutual_id)
            
            if periodo_id != 0:
                queryset = queryset.filter(periodo__pk=periodo_id)

        except (ValueError, TypeError):
            mutual_id = None

        
        if filter_form.is_valid() :
            es_borrador = filter_form.cleaned_data.get('es_borrador')

            if es_borrador is not None:
                queryset = queryset.filter(es_borrador=es_borrador)

            queryset = queryset.order_by('periodo__mes_anio', 'mutual__cuit', 'fecha_lectura')

        return queryset

class DeclaracionJuradaFilterForm(forms.Form):
    es_borrador = forms.BooleanField(required=False)



    

@login_required(login_url="/login/")
@permission_required('empleadospublicos.permission_empleado_publico', raise_exception=True)
def leerDeclaracionJurada(request):
    if request.method == 'POST':
        declaracion_id_check = request.POST.getlist('declaracion_leidos')
        declaraciones = DeclaracionJurada.objects.filter(id__in=declaracion_id_check)
        
        # Establecer valores comunes independientemente de la acción
        es_leida = True if request.POST.get('accion') == '1' else False
        fecha_lectura = datetime.now() if es_leida else None

        # Aplicar cambios a todas las declaraciones
        for declaracion in declaraciones:
            if declaracion.es_leida != es_leida: 
                declaracion.es_leida = es_leida
                declaracion.fecha_lectura = fecha_lectura
                declaracion.save()

        messages.success(request, f'Declaraciones Juradas {"leídas" if es_leida else "marcadas como no leídas"} con éxito.')
        return redirect('mutual:periodo_vigente_detalle')

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



@login_required(login_url="/login/")
def verificar_todas_leidas(request, periodo_pk):
    print("estoyen verificarPeriodo")
    #Obtengo el periodo
    

    # declaraciones = DeclaracionJurada.objects.all()
    # # declaraciones = DeclaracionJurada.objects.filter(periodo=periodo_actual)

    # # Verifica si todas las declaraciones están marcadas como leídas
    # todas_leidas = all(declaracion.es_leida for declaracion in declaraciones)

    # Devuelve el resultado en formato JSON
    # return JsonResponse({'todas_leidas': todas_leidas})

    # declaracion = get_object_or_404(DeclaracionJurada, pk=pk)
    # declaracion.es_leida = True
    # declaracion.fecha_lectura = datetime.now()
    # declaracion.save()
    # print("DECLARACION JURADA ", declaracion)


def es_siguiente_mes(periodo_anterior, periodo_creado):
    
    print(periodo_anterior.month)
    print(periodo_creado.month)

    print(periodo_anterior.month + 1)
    print(periodo_creado.month + 1)

    return periodo_creado.year == periodo_anterior.year and periodo_creado.month == periodo_anterior.month

class PeriodoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Periodo
    form_class = FormularioPeriodo
    template_name = 'periodo_alta.html'
    success_url = reverse_lazy('mutual:mutual_crear')
    login_url = "/login/"
    permission_required = "empleadospublicos.permission_empleado_publico"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = Periodo.objects.all()

        context['titulo'] = 'Alta de Periodo'
        context['habilitado'] = True

        # Verificar si hay periodos y obtener el último periodo creado
        if periodos.exists():
            ultimo_periodo = periodos.latest('fecha_inicio')

            # Verificar si el último periodo tiene fecha_fin
            if ultimo_periodo.fecha_fin is None:
                print("ULTIMO PERIODO")
                context['habilitado'] = False
                context['titulo'] = 'El último periodo vigente no ha finalizado'

        return context

    def form_valid(self, form):

        periodos = Periodo.objects.all()
        fecha_inicio = form.cleaned_data["fecha_inicio"]

        if periodos.exists():

            #Obtengo el ultimo periodo creado por fecha de inicio
            ultimo_periodo = periodos.latest('fecha_inicio')
            #obtengo el mes de inicio
            #compario si el mes_anio del ultimo periodo es igual del mes anio que mi fecha de creacion
            if not fecha_es_mayor_por_meses(ultimo_periodo.mes_anio):
                if (ultimo_periodo.mes_anio.month == fecha_inicio.month ):
                    if (ultimo_periodo.mes_anio.month == 12 ):
                        mes_anio = datetime(ultimo_periodo.mes_anio.year+1, 1, 1 ).date()
                    else:
                        mes_anio = datetime(ultimo_periodo.mes_anio.year, ultimo_periodo.mes_anio.month+1 , 1 ).date()
                else:
                    # Si son distintos, entonces comparo si el siguiente mes corresponde al mes de mi fecha de inicio
                    if (ultimo_periodo.mes_anio.month == 12 ):
                        
                        if (fecha_inicio.month == 1 ):
                            mes_anio = datetime(ultimo_periodo.mes_anio.year+1, 1 , 1 ).date()
                    else:
                        if (ultimo_periodo.mes_anio.month + 1 == fecha_inicio.month ):
                            mes_anio = datetime(ultimo_periodo.mes_anio.year, fecha_inicio.month , 1 ).date()
                        else:
                            messages.error(self.request, 'La fecha de inicio no sigue una correlacion con el periodo anterior.')
                            return super().form_invalid(form)
            else:
                mes_anio = datetime(fecha_inicio.year, fecha_inicio.month , 1 ).date()
 
        else:
            mes_anio = datetime(fecha_inicio.year, fecha_inicio.month , 1 ).date()

        periodo = form.save(commit=False)
        periodo.mes_anio = mes_anio
        periodo.save()
            
        response = super().form_valid(form)
        messages.success(self.request, f'Periodo creado exitosamente.')

        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al momento de completar el formulario.')
        return super().form_invalid(form)

class PeriodoVigenteDeclaracionFilterForm(forms.ModelForm):
    es_leida = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Leídos'  # Set the custom label here
    )

    class Meta:
        model = DeclaracionJurada
        fields = ['es_leida']


@login_required(login_url="/login/")
@permission_required('empleadospublicos.permission_empleado_publico', raise_exception=True)
def periodoVigenteDetalle(request):

    # Obtenemos el último periodo que no tiene fecha de fin
    periodo = Periodo.objects.filter(fecha_fin__isnull=True).first()
    
    # Si no hay un periodo, redirige a una página específica
    if not periodo:
        messages.warning(request, "No tiene un periodo vigente.")
        return redirect('mutual:periodo_crear')

    titulo = 'Periodo Vigente'

    # Obtenemos todas las declaraciones juradas presentadas en el periodo
    declaraciones = DeclaracionJurada.objects.filter(periodo=periodo, es_borrador=False)

    # Obtenemos las mutuales asociadas a esas declaraciones juradas
    mutuales_en_declaraciones = declaraciones.values_list('mutual', flat=True).distinct()

    # Luego, puedes obtener los objetos de las mutuales correspondientes
    mutuales_presentes = Mutual.objects.filter(id__in=mutuales_en_declaraciones)

    # mutuales = [declaracion.mutual for declaracion in page_obj]


    # Handle form submission
    if request.method == 'POST':
        form = PeriodoVigenteDeclaracionFilterForm(request.POST)
        if form.is_valid():
            es_leida_value = form.cleaned_data['es_leida']
            mutual_id = request.POST.get('enc_mutual')
            try:
                mutual_id = int(mutual_id)
                if mutual_id != 0: 
                    declaraciones = declaraciones.filter(mutual__pk=mutual_id)
            except (ValueError, TypeError):
                mutual_id = None
            finally:
                if es_leida_value:
                    declaraciones = declaraciones.filter(es_leida=es_leida_value)
    else:
        form = PeriodoVigenteDeclaracionFilterForm()

    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(declaraciones, 10)  # Show 10 declarations per page
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


    context = {
        'periodo': periodo,
        'page_obj': page_obj,
        'mutuales': mutuales_presentes,
        'titulo': titulo,
        'form': form,
    }
    return render(request, 'periodo_vigente_detalle.html', context)

def validar_declaraciones_leidas(request, declaraciones, redirect_url):
    for declaracion in declaraciones:
        if not declaracion.es_leida:
            messages.error(request, "El periodo vigente tiene declaraciones que no han sido leídas aún.")
            return False
    return True

def finalizar_periodo(request, pk, crear_nuevo=False):
    periodo = get_object_or_404(Periodo, pk=pk)
    declaraciones = DeclaracionJurada.objects.filter(periodo=periodo)

    todas_leidas = validar_declaraciones_leidas(request, declaraciones, 'mutual:periodo_vigente_detalle')


    if todas_leidas:
        periodo.fecha_fin = datetime.today()
        periodo.save()
        if crear_nuevo:
            fecha_inicio = periodo.fecha_fin
            mes_anio = fecha_inicio + relativedelta(months=1)

            periodo_nuevo = Periodo(fecha_inicio=fecha_inicio, mes_anio=mes_anio)
            periodo_nuevo.save()

            messages.info(request, "Periodo finalizado y se ha creado un periodo nuevo.")
            return redirect('mutual:periodo_vigente_detalle')

        messages.info(request, "Periodo finalizado con éxito.")
        return redirect('mutual:historico')
    else:
        return redirect('mutual:periodo_vigente_detalle')


def finalizarPeriodo(request, pk):
    return finalizar_periodo(request, pk)

@login_required(login_url="/login/")
@permission_required('empleadospublicos.permission_empleado_publico', raise_exception=True)
def EditarMutal(request, pk):
     if request.method == 'POST':
        data = request.POST
        # print(data)
        m = Mutual.objects.get(pk = pk)
        
        nombre = data.get('nombre')
        cuit = data.get('cuit')
        alias = data.get('alias')
        

        if len(cuit) != 11:
            messages.warning(request, "Cuit invalido, debe tener 11 caracteres")
            return redirect('mutual:listado_mutual')
        else:
            m.cuit = cuit
          
        if m.nombre != nombre:
            try: 
               Mutual.objects.get(nombre = nombre)
               messages.warning(request, "El Nombre de mutual ya existe")
               return redirect('mutual:listado_mutual')
            except Mutual.DoesNotExist:
               m.nombre = nombre
               
        if m.alias != alias:
            try: 
               Mutual.objects.get(alias = alias)
               messages.warning(request, "El alias de mutual ya existe")
               return redirect('mutual:listado_mutual')
            except Mutual.DoesNotExist:
               m.alias = alias
       
      
            
         
        origenr = data.get('origen_r')
        destinor = data.get('destino_r')
        concep1r = data.get('concep1_r')
        concep2r = data.get('concep2_r')
        
  
        if data.get('activo') == "on":
            activo = True
        else: 
            activo = False
        
        if m.activo != activo:
           m.activo = activo
        
        if data.get('origen_r') :
           print("entre")
           try:
              reclamo = m.detalle.all().get(tipo = 'R')
              reclamo.origen = data.get('origen_r')
              if reclamo.destino != data.get('destino_r') : 
                  reclamo.destino = data.get('destino_r')
                  
              concepto = int(data.get('concep1_r'))    
              if reclamo.concepto_1 != concepto:
                 print(" soy distinto") 
                 print( reclamo.concepto_1.object )
                 print(concepto.object)
                 if concepto > 1:
                    if DetalleMutual.objects.filter(concepto_2 = concepto).exists() or  DetalleMutual.objects.filter(concepto_1 = concepto).exists() :
                        messages.error(request, "concepto 1 de detll.reclamo ingresado pertecene a otra mutual")
                        return redirect('mutual:listado_mutual')
                 reclamo.concepto_1 = concepto    
              else:
                  print("soy igual")      
                 
              concepto = int(data.get('concep2_r'))
              if reclamo.concepto_2 != concepto:
                 print("soy distinto concepto2 reclamo")
         
                 
                 if concepto == reclamo.concepto_1:
                     messages.error(request, "Concepto 2 de detalle reclamo no puede ser igual a concepto 1")
                     return redirect('mutual:listado_mutual')
                 
                 
                 if concepto > 1:
                    if DetalleMutual.objects.filter(concepto_2 = concepto).exists() or  DetalleMutual.objects.filter(concepto_1 = concepto).exists() :
                        messages.error(request, "Edicion cancelada, el concepto 2 ingresado  detalle reclamo Pertenece a una mutual")
                        return redirect('mutual:listado_mutual')
                 reclamo.concepto_2 = concepto
              else:
                print("soy igual concepto2 reclamo")
                                 
            
             
              
              reclamo.save()
           except:
              print("exept 1") 
        
        if data.get('origen_p') :
           print("entre")
           try:
              prestamo = m.detalle.all().get(tipo = 'P')
              prestamo.origen = data.get('origen_p')
              if prestamo.destino != data.get('destino_p') : 
                  prestamo.destino = data.get('destino_p')
              
              concepto = int(data.get('concep1_p')) 
              if prestamo.concepto_1 != concepto:
                 concepto = data.get('concep1_p')
                 if concepto > 1:
                    if DetalleMutual.objects.filter(concepto_2 = concepto).exists() or  DetalleMutual.objects.filter(concepto_1 = concepto).exists() :
                        messages.error(request, "Edicion cancelada, el concepto 1 ingresado en detalle reclamo Pertenece a una mutual")
                        return redirect('mutual:listado_mutual')
                 prestamo.concepto_1 = concepto    
                 
                 
              concepto = int(data.get('concep2_p'))   
              if prestamo.concepto_2 != concepto:
                 print("soy distinto prestamo")
                 
                 if concepto == prestamo.concepto_1:
                     messages.error(request, "Edicion cancelada, el concepto 2 ingresado en detalle prestamo Pertenece a una mutual")
                     return redirect('mutual:listado_mutual')
                 if concepto > 1:
                    print("entre a buscar en filtro")
                    if DetalleMutual.objects.filter(concepto_2 = concepto).exists() or  DetalleMutual.objects.filter(concepto_1 = concepto).exists() :
                        messages.error(request, "Concepto 2 de detalle prestamo ingresado pertecene a otra mutual")
                        return redirect('mutual:listado_mutual')
                 prestamo.concepto_2 = concepto
              
              prestamo.save()
           except Exception:
               print("except")
               print(Exception)
               
              
            
        
        m.save()
        print("llegue aqui")
        messages.success(request, "Mutual actualizada éxitosamente")
        return redirect('mutual:listado_mutual')
            
         



@login_required(login_url="/login/")
@permission_required('empleadospublicos.permission_empleado_publico', raise_exception=True)
def finalizarPeriodoCrearNuevo(request, pk):
    return finalizar_periodo(request, pk, crear_nuevo=True)

