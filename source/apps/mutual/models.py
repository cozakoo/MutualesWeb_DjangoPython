import calendar
from django.db import models
from django.core.validators import MaxValueValidator
import uuid
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import os

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

##-------------------- DECLARACION JURADA Y DETALLE ---------------------
class DetalleDeclaracionJurada(models.Model):
    
    TIPO = [
        ('P', 'prestamo'),
        ('R', 'reclamo'),
    ]
    
    tipo = models.CharField(max_length=1, choices=TIPO)
    importe = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    archivo = models.FileField(upload_to='documentos/')
    total_registros= models.IntegerField(default=0)  # Nuevo campo

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
class Periodo(models.Model):
    """
    Antes de crear un nuevo periodo se revisa si el periodo anterior tiene fecha de fin
    """
    fecha_inicio = models.DateField()   # puede o no estar en el mes anterior
    fecha_fin = models.DateField(null = True , blank=True)      # tiene que estar dentro del mes
    mes_anio = models.DateField()       # mes y año del periodo. EJ: 01/01/2024 corresponde a ENERO
    
    def obtener_nombre_mes(self):
        # Utiliza el atributo month de mes_anio para obtener el número del mes
        numero_mes = self.mes_anio.month
        # Utiliza el atributo year de mes_anio para obtener el año
        año = self.mes_anio.year
        # Utiliza el módulo calendar para obtener el nombre del mes en inglés
        nombre_mes_ingles = calendar.month_name[numero_mes]
        
        # Traducción simple a español
        traducciones_meses = {
            'january': 'enero',
            'february': 'febrero',
            'march': 'marzo',
            'april': 'abril',
            'may': 'mayo',
            'june': 'junio',
            'july': 'julio',
            'august': 'agosto',
            'september': 'septiembre',
            'october': 'octubre',
            'november': 'noviembre',
            'december': 'diciembre',
        }
        
        # Obtén el nombre del mes en español desde el diccionario de traducciones
        nombre_mes_espanol = traducciones_meses.get(nombre_mes_ingles.lower(), nombre_mes_ingles.lower())
        
        # Devuelve una cadena que incluye el nombre del mes en español y el año
        return f"{nombre_mes_espanol.capitalize()} {año}"  # Capitaliza la primera letra del mes
    
    
    def __str__(self):
        return self.obtener_periodo_numerico()
    
    def __str__YYYYMM__(self):
        return self.obtener_periodo_numerico()
    

    def obtener_periodo_numerico(self):
        # Obtén el año y el mes como cadenas
        año = str(self.mes_anio.year)
        mes = str(self.mes_anio.month).zfill(2)  # Asegura que el mes tenga 2 dígitos (con ceros a la izquierda si es necesario)
        
        # Devuelve el año y el mes concatenados en formato YYYYMM
        print("AÑO + MES", año + mes)
        return año + mes


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
    
