from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from apps.mutual.models import Mutual
from apps.users.models import UserRol

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
    print("-----------")
    term = request.GET.get('q')  # Obtener el término de búsqueda de la solicitud GET

    # Realizar la búsqueda en la base de datos
    mutuales = Mutual.objects.filter(nombre__icontains=term)

    # Construir una lista de resultados JSON con datos completos de Mutual
    results = [{'id': mutual.id, 'alias': mutual.alias, 'cuit': mutual.cuit, 'nombre': mutual.nombre} for mutual in mutuales]

    # Devolver los resultados como una respuesta JSON
    return JsonResponse(results, safe=False)