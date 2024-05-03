import calendar
from django.db import models
from django.core.validators import MaxValueValidator
import uuid
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.timezone import now
import os

# class AcuseRecibo(models.Model):
#     codigo = codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
##-------------------- MUTUAL Y DETALLE ---------------------
class DetalleMutual(models.Model):
    TIPO_DECLARACION = [
        ('R', 'reclamo'),
        ('P', 'préstamo'),
    ]
    tipo = models.CharField(max_length=1 , choices=TIPO_DECLARACION)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    concepto_1 = models.IntegerField(null = True , blank=True)
    concepto_2 = models.IntegerField(null = True , blank=True)

class Mutual(models.Model):

    nombre = models.CharField(max_length=255) #nombre formal legalemte
    alias = models.CharField(max_length=50)  # Alias utilizado legalmente
    cuit = models.CharField(max_length=11,  unique=True)  
    activo = models.BooleanField(default=True)
    # fecha_subida = models.DateField(auto_now_add=True, blank=True)
    detalle = models.ManyToManyField(DetalleMutual) 

    def __str__(self):
        return self.alias
    
    def obtener_ultimo_periodo_presentado(self):
        declaracionesPresentadas = DeclaracionJurada.objects.all().filter(mutual=self)

        if declaracionesPresentadas.exists():
            ultimo_periodo_presentado = declaracionesPresentadas.last().periodo
            return ultimo_periodo_presentado.mes_anio.strftime('%Y-%m')
        else:
            return ""
        
        
        
@receiver(pre_delete, sender=Mutual)
def delete_related_detalle_mutual(sender, instance, **kwargs):
    instance.detalle.all().delete()


def archivo_path(instance, filename):
    # Obtén la extensión del archivo
    base, extension = filename.rsplit('.', 1)
    # Obtén la fecha actual en el formato deseado
    fecha_actual = now().strftime('%Y%m%d')
    # Construye el nuevo nombre del archivo
    nuevo_nombre = f"{base}_({fecha_actual}).{extension}"
    return f'documentos/{nuevo_nombre}'


           
##-------------------- DECLARACION JURADA Y DETALLE ---------------------
class DetalleDeclaracionJurada(models.Model):
    
    TIPO = [
        ('P', 'préstamo'),
        ('R', 'reclamo'),
    ]
    
    tipo = models.CharField(max_length=1, choices=TIPO)
    importe = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    archivo = models.FileField(upload_to=archivo_path)
    total_registros= models.IntegerField(default=0)  # Nuevo campo
    concepto = models.IntegerField(null = True , blank=True)

    def obtenerImporteConMillares(self):
        miles_translator = str.maketrans(".,", ",.")
        # self.importe = "{:,}".format(self.importe).translate(miles_translator)
        return "{:,}".format(self.importe).translate(miles_translator)

@receiver(pre_delete, sender=DetalleDeclaracionJurada)
def eliminar_archivo(sender, instance, **kwargs):
    # Verifica si existe un archivo asociado y elimínalo
    if instance.archivo:
        if os.path.isfile(instance.archivo.path):
            os.remove(instance.archivo.path)





#-------------------- PERIODO ---------------------
from datetime import datetime

class Periodo(models.Model):
    """
    Antes de crear un nuevo periodo se revisa si el periodo anterior tiene fecha de fin
    """
    fecha_inicio = models.DateField()   # puede o no estar en el mes anterior
    fecha_fin = models.DateField(null = True , blank=True)      # tiene que estar dentro del mes
    mes_anio = models.DateField()       # mes y año del periodo. EJ: 01/01/2024 corresponde a ENERO
    

    def __str__(self):
        return datetime.strftime(self.mes_anio, "%Y%m")
    

class DeclaracionJurada(models.Model):
    mutual = models.ForeignKey(Mutual, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    detalles = models.ManyToManyField(DetalleDeclaracionJurada,related_name='detalles', blank=True, through = "DeclaracionJuradaDetalles")
    fecha_subida = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # fecha creación del borrador
    rectificativa = models.IntegerField(default=0)
    codigo_acuse_recibo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    es_leida = models.BooleanField(default=False)
    es_borrador = models.BooleanField(default=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

class DeclaracionJuradaDetalles(models.Model):
    declaracionJurada = models.ForeignKey(DeclaracionJurada, on_delete=models.CASCADE)
    detalleDeclaracionJurada = models.ForeignKey(DetalleDeclaracionJurada, on_delete=models.CASCADE)
    
