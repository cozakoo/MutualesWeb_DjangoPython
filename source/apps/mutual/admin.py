from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Mutual)
admin.site.register(models.DeclaracionJurada)
admin.site.register(models.DetalleMutual)
admin.site.register(models.DetalleDeclaracionJurada)