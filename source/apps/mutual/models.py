from django.db import models

# Create your models here.

class Mutual(models.Model):

    nombre = models.CharField(max_length=100)
    cuit = models.CharField(max_length=30)
    estado = models.BooleanField()
    fecha_subida = models.DateField(auto_now_add=True, blank=True)
    
    def __str__(self):
        return self.name
    
    