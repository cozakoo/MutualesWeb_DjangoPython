from django.db import models
from django.core.validators import MaxValueValidator
import uuid

# Create your models here.


# class AcuseRecibo(models.Model):
#     codigo = codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    

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
    cuit = models.CharField(max_length=11, validators=[MaxValueValidator(99999999999)])
    activo = models.BooleanField(default=True)
    # fecha_subida = models.DateField(auto_now_add=True, blank=True)
    detalle = models.ManyToManyField(DetalleMutual) 

    def __str__(self):
        return self.nombre
    

##-------------------- DECLARACION JURADA Y DETALLE ---------------------
class DeclaracionJurada(models.Model):
    mutual = models.ForeignKey(Mutual, on_delete=models.CASCADE)
    fecha_subida = models.DateField()
    periodo = models.DateField()
    rectificativa = models.IntegerField(default=0)
    codigo_acuse_recibo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    leida = models.BooleanField(default=False)

class DetalleDeclaracionJurada(models.Model):
    TIPO = [
        ('P', 'prestamo'),
        ('R', 'reclamo'),
    ]
    declaracion_jurada = models.ForeignKey(DeclaracionJurada, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    archivo = models.FileField(upload_to='documentos/')
    total_registros= models.IntegerField(default=0)  # Nuevo campo
##-----------------------------------------------------------------------
