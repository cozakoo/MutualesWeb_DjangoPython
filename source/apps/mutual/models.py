from django.db import models
from django.core.validators import MaxValueValidator
import uuid

# class AcuseRecibo(models.Model):
#     codigo = codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
##-------------------- MUTUAL Y DETALLE ---------------------
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
    cuit = models.CharField(max_length=11)
    activo = models.BooleanField(default=True)
    # fecha_subida = models.DateField(auto_now_add=True, blank=True)
    detalle = models.ManyToManyField(DetalleMutual) 

    def __str__(self):
        return self.nombre

##-------------------- DECLARACION JURADA Y DETALLE ---------------------
class DetalleDeclaracionJurada(models.Model):
    
    TIPO = [
        ('P', 'prestamo'),
        ('R', 'reclamo'),
    ]
    
    tipo = models.CharField(max_length=1, choices=TIPO)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    archivo = models.FileField(upload_to='documentos/')
    total_registros= models.IntegerField(default=0)  # Nuevo campo

#-------------------- PERIODO ---------------------
class Periodo(models.Model):
    """
    Antes de crear un nuevo periodo se revisa si el periodo anterior tiene fecha de fin
    """
    fecha_inicio = models.DateField()   # puede o no estar en el mes anterior
    fecha_fin = models.DateField(null = True , blank=True)      # tiene que estar dentro del mes
    mes_anio = models.DateField()       # mes y año del periodo. EJ: 01/01/2024 corresponde a ENERO


class DeclaracionJurada(models.Model):
    mutual = models.ForeignKey(Mutual, on_delete=models.CASCADE)
    fecha_subida = models.DateField()
    fecha_creacion = models.DateField(auto_now_add=True) # fecha creación del borrador
    rectificativa = models.IntegerField(default=0)
    codigo_acuse_recibo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    es_leida = models.BooleanField(default=False)
    es_borrador = models.BooleanField(default=True)
    
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    detalles = models.ManyToManyField(DetalleDeclaracionJurada,related_name='detalles', blank=True, through = "DeclaracionJuradaDetalles")


class DeclaracionJuradaDetalles(models.Model):
    declaracionJurada = models.ForeignKey(DeclaracionJurada, on_delete=models.CASCADE)
    detalleDeclaracionJurada = models.ForeignKey(DetalleDeclaracionJurada, on_delete=models.CASCADE)