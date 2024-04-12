from django.shortcuts import render

from django.views.generic import TemplateView
from datetime import datetime
from collections import Counter
from django.db.models import Count
from django.shortcuts import get_object_or_404

from apps.mutual.models import DeclaracionJurada, Mutual
from django.db.models import Sum
from django.utils import formats

class reporteMutualDeclaracionesJuradasView(TemplateView):
    template_name = 'reporte_mutuales_declaraciones.html'
    
    def get_graph_mutual(self, mutual):
        declaraciones = DeclaracionJurada.objects.filter(mutual=mutual)
        
        reclamos = []
        prestamos = []
        categorias = []
        if declaraciones.exists():
            for declaracion in declaraciones:
                fecha = declaracion.periodo.mes_anio.strftime('%Y-%m')  # Formatear la fecha como una cadena
                categorias.append(fecha)
                
                importe_reclamo = float(declaracion.detalles.filter(tipo='R').first().importe) if declaracion.detalles.filter(tipo='R').first() else 0
                importe_prestamo = float(declaracion.detalles.filter(tipo='P').first().importe) if declaracion.detalles.filter(tipo='P').first() else 0
                
                reclamos.append(importe_reclamo)
                prestamos.append(importe_prestamo)
                
        return categorias, reclamos, prestamos
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mutual_id = self.kwargs.get('mutual_id')
        mutual = get_object_or_404(Mutual, pk=mutual_id)

        categorias, reclamos, prestamos = self.get_graph_mutual(mutual)

        context['titulo'] = f"MUTUAL {mutual.nombre} Y SUS DECLARACIONES JURADAS PRESENTADAS"
        context['categorias'] = categorias
        context['reclamos'] = reclamos
        context['prestamos'] = prestamos
        context['mutual_id'] = mutual_id  # Pass mutual_id to JavaScript
        return context