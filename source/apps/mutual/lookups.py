from __future__ import unicode_literals

from selectable.base import ModelLookup
from selectable.registry import registry

from .models import Mutual


class MutualLookup(ModelLookup):
    model = Mutual
    search_fields = ('alias__icontains', )
    
registry.register(MutualLookup)