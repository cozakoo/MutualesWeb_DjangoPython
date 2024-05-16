from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry

from .models import Mutual, Periodo



class MutualLookup(ModelLookup):
    model = Mutual
    search_fields = ('alias__icontains', )
    
    def get_query(self, request, term):
        queryset = super().get_query(request, term)
        # Ordenar por alias y luego por posición, y limitar a los primeros 5 resultados
        return queryset.order_by('alias')[:5] 

registry.register(MutualLookup)

class PeriodoLookup(ModelLookup):
    model = Periodo
    search_fields = ('mes_anio__icontains', )

    def get_query(self, request, term):
        queryset = super().get_query(request, term)
        return queryset.order_by('mes_anio')[:7] 

registry.register(PeriodoLookup)

class PeriodosFinalizadosLookup(ModelLookup):
    model = Periodo
    search_fields = ('mes_anio__icontains', )

    def get_query(self, request, term):
        queryset = super().get_query(request, term)
        queryset = queryset.exclude(fecha_fin__isnull=True)
        return queryset.order_by('mes_anio')[:7] 

registry.register(PeriodosFinalizadosLookup)
