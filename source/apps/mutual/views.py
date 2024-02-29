from io import BytesIO
import io
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import FileResponse
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
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
    # success_url = reverse_lazy('mutual:declaracion_jurada')

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if 'confirmacion' in request.POST:

           mutual = obtenerMutualVinculada(self)
           if existeBorrador(self) :
            try:
                periodo = obtenerPeriodoVigente(self)
                djs = DeclaracionJurada.objects.filter(mutual = mutual , es_borrador = False, periodo = periodo)
                for dj in djs:
                    dj.detalles.all().delete()
                    dj.delete()
            except DeclaracionJurada.DoesNotExist:
                print("omite")
            
            try:
                    
                    dj = DeclaracionJurada.objects.get(mutual = mutual , es_borrador = True)
                    dj.es_borrador = False
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
        
        
        print(request.user.get_all_permissions)
          
        if periodo == None:
            print("redirijo msj")
            msj = ("No existe un Periodo de Declaración Jurada disponible actualmente.")
            contexto = {'msj': msj}
            return render(request, 'msj_informativo.html', contexto)
        
        # try:
        #  dj = DeclaracionJurada.objects.get(es_borrador = False,  periodo = periodo )
        #  print("aviso se va rectificar")
        # except DeclaracionJurada.DoesNotExist:
        #     print("Se puede declarar o rectificar")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accion = self.kwargs.get('accion')

        if accion == 'rectificar':
            context['titulo'] = 'Declaración Rectificativa'
        else:
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
                        periodo = periodoActual
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
         

            if fecha_obj_inicio > periodoActual.mes_anio:
                listErrores.append(f"Error: La FECHA INICIO en la línea {line_number} es mayor que la fecha inicial del periodo. Línea: {line_content}")

            if fecha_obj_fin < periodoActual.mes_anio:
                listErrores.append(f"Error: La FECHA FIN en la línea {line_number} es menor mayor que la fecha inicial del periodo. Línea: {line_content}")

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
                    self.validar_fecha_reclamo(line_content, line_number, 31, 39, "FECHA INICIO",listErrores)
                    self.validar_fecha_reclamo:(line_content, line_number, 39, 47, "FECHA FIN", listErrores) # type: ignore
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

    def validar_fecha_reclamo(self, line_content, line_number, inicio, fin, tipo_fecha, listErrores):
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
                listErrores.append(mensaje_error)

        except ValueError:
            listErrores.append(f"Error: La {tipo_fecha.lower()} en la línea {line_number} no es válida. Línea: {line_content}")
            # messages.warning(self.request, mensaje_error)


class DetalleMutualView(LoginRequiredMixin, DetailView):
    login_url = '/login/'
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

class HistoricoView(ListView):
    model = DeclaracionJurada
    template_name = "dj_list.html"
    paginate_by = 10# Número de elementos por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Historico'
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

def descargarDeclaracion(request, pk):
    declaracion = get_object_or_404(DeclaracionJurada, pk=pk)
    buffer = generate_pdf(declaracion)

    return FileResponse(buffer, as_attachment=True, filename="declaracion_jurada.pdf")




class MutualesListView(ListView):
    model = Mutual
    template_name = "mutuales_listado.html"
    paginate_by = 10# Número de elementos por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mutuales'
        return context
    
    def get_queryset(self):
        # Filtrar los objetos según tu lógica
        queryset = Mutual.objects.all()
        print("LISTADO DE MUTUALES")
        print(queryset)
        # Devolver el queryset filtrado
        return queryset

class DeclaracionJuradaDeclaradoListView(ListView):
    model = DeclaracionJurada
    template_name = "dj_declarados_list.html"
    paginate_by = 10  # Número de elementos por página

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Historico'
        context['filter_form'] = DeclaracionJuradaFilterForm(self.request.GET)
        return context

    def get_queryset(self):
        # Obtener el queryset original sin filtrar
        queryset = DeclaracionJurada.objects.all()

        # Obtener los datos del formulario enviado por el usuario
        filter_form = DeclaracionJuradaFilterForm(self.request.GET)

        # Validar el formulario y aplicar filtros si es válido
        if filter_form.is_valid():
            es_borrador = filter_form.cleaned_data.get('es_borrador')
            mutual = filter_form.cleaned_data.get('mutual')  
            periodo = filter_form.cleaned_data.get('periodo')

            # Aplicar filtros al queryset
            if es_borrador is not None:
                queryset = queryset.filter(es_borrador=es_borrador)

            # Filtrar por mutual
            if mutual:
                queryset = queryset.filter(mutual=mutual)

            # Filtrar por periodo
            if periodo:
                queryset = queryset.filter(periodo=periodo)

        return queryset

class DeclaracionJuradaFilterForm(forms.Form):
    mutual = forms.ModelChoiceField(queryset=Mutual.objects.all(), required=False, empty_label="Todas las mutuales")
    periodo = forms.ModelChoiceField(queryset=Periodo.objects.all(), required=False, empty_label="Todos los periodos")
    es_borrador = forms.BooleanField(required=False)




    
from django.http import JsonResponse

def leerDeclaracionJurada(request):
    if request.method == 'POST':
        declaraciones_ids = request.POST.getlist('declaracion_leidos')
        declaraciones = DeclaracionJurada.objects.filter(id__in=declaraciones_ids)

        for declaracion in declaraciones:
            declaracion.es_leida = True
            declaracion.fecha_lectura = datetime.now()
            declaracion.save()

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


    # declaracion = get_object_or_404(DeclaracionJurada, pk=pk)
    # declaracion.es_leida = True
    # declaracion.fecha_lectura = datetime.now()
    # declaracion.save()
    # print("DECLARACION JURADA ", declaracion)



