from django.db import models

# Create your models here.

class DetalleMutual(models.Model):
    TIPO_DECLARACION = [
        ('R', 'reclamo'),
        ('P', 'prestamo'),
    ]
    tipo = models.CharField(max_length=1 , choices=TIPO_DECLARACION)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    concepto_1 = models.IntegerField()
    concepto_2 = models.IntegerField()



class Mutual(models.Model):

    nombre = models.CharField(max_length=100)
    cuit = models.BigIntegerField()
    activo = models.BooleanField(default=True)
    # fecha_subida = models.DateField(auto_now_add=True, blank=True)
    detalle = models.ManyToManyField(DetalleMutual) 
   
    
    def __str__(self):
        return self.nombre
    
        

class DeclaracionJurada(models.Model):
    TIPO_DECLARACION = [
        ('R', 'reclamo'),
        ('P', 'prestamo'),
    ]
    MESES_CHOICES = [
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ]
# si no fue leida, podes rectificarla
    mutual = models.ForeignKey(Mutual, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_DECLARACION)
    # fecha_subida = models.DateField()
    # fecha_rectificacion = models.DateField()
    periodo_mes = models.CharField(max_length=2, choices=MESES_CHOICES)
    # periodo_anio = models.IntegerField()  # Puedes usar un IntegerField para el año
    archivo = models.FileField(upload_to='documentos/')