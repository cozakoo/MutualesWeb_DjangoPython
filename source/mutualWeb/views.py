from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from apps.mutual.models import Mutual
from apps.users.models import UserRol
from mutualWeb import settings

@login_required(login_url="/login/")
def dashboard(request):
  
    user =  request.user
    userRol = UserRol.objects.get(user = user )
    if request.method == 'GET' :
        if not userRol.ultimaConexion:
            userRol.ultimaConexion =  timezone.now()
            
        contexto = {
            'rol': userRol.rol,
            'ultimaConexion': userRol.ultimaConexion,
        }
        
        if  userRol.rol.persona.es_cliente: 
            return render(request, 'dashboardCliente.html',contexto)
        
        if  userRol.rol.persona.es_empleado_publico: 
            return render(request, 'dashboardEmpleadoPublico.html',contexto)
    
        if userRol.rol.persona.es_admin:
                return render(request, 'dashboardAdministrador.html',contexto)
        
        return redirect('users:login')


def pagina_no_encontrada(request, exception):
   return redirect('dashboard')


def buscar_mutuales(request):
    term = request.GET.get('q')  # Obtener el término de búsqueda de la solicitud GET
    # Realizar la búsqueda en la base de datos
    mutuales = Mutual.objects.filter(nombre__icontains=term)
    # Construir una lista de resultados JSON con datos completos de Mutual
    results = [{'id': mutual.id, 'alias': mutual.alias, 'cuit': mutual.cuit, 'nombre': mutual.nombre} for mutual in mutuales]
    # Devolver los resultados como una respuesta JSON
    return JsonResponse(results, safe=False)

from django.http import FileResponse
import os

@login_required(login_url='/login/')
def abrir_pdf(request, nombre_archivo, nombre_mostrado):
    # Ruta al archivo PDF en tu sistema
    ruta_pdf = os.path.join(settings.BASE_DIR, '..', 'documentation', nombre_archivo)

    try:
        if os.path.exists(ruta_pdf):
            response = FileResponse(open(ruta_pdf, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{nombre_mostrado}"'
            return response
        else:
            return HttpResponse('El archivo PDF no se encontró.', status=404)
    except Exception as e:
        return HttpResponse(f'Error al abrir el archivo PDF: {str(e)}', status=500)


@login_required(login_url="/login/")
def abrirManualMutual(request):
    return abrir_pdf(request, 'Guía de Usuario del SGM para Mutuales.pdf', 'Guía de Usuario del SGM para Mutuales.pdf')

@login_required(login_url="/login/")
def abrirManualOperativos(request):
    return abrir_pdf(request, 'Guía de Usuario del SGM para Operativos.pdf', 'Guía de Usuario del SGM para Mutuales.pdf')

@login_required(login_url="/login/")
def abrirManualAdministrador(request):
    return abrir_pdf(request, 'Guía de Usuario del SGM para Administradores.pdf', 'Guía de Usuario del SGM para Mutuales.pdf')
