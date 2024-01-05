from django.db import models

# Create your models here.

class Mutual(models.Model):

    nombre = models.CharField(max_length=100)
    cuit = models.CharField(max_length=30)
    estado = models.BooleanField()
    fecha_subida = models.DateField(auto_now_add=True, blank=True)

    
    def __str__(self):
        return self.name

class DeclaracionJurada(models.Model):
    
    TIPO_DECLARACION = [
        ('R', 'reclamo'),
        ('P', 'prestamo'),
    ]
    mutual = models.ForeignKey(Mutual,on_delete = models.CASCADE)
    tipo = models.CharField(max_length=1 , choices=TIPO_DECLARACION)
    fecha_subida = models.DateField()
    fecha_rectificacion = models.DateField()
    periodo_declarado = models.DateField()
    

