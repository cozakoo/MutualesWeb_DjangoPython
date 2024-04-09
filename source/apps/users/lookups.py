from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry
from django.contrib.auth.models import User

class UsernameLookup(ModelLookup):
    model = User
    search_fields = ('username__icontains', )
    
    def get_query(self, request, term):
        queryset = super().get_query(request, term)
        # Ordenar por alias y luego por posición, y limitar a los primeros 5 resultados
        return queryset.order_by('username')[:5] 

registry.register(UsernameLookup)
