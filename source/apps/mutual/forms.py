from django import forms
from apps.mutual.lookups import MutualLookup, PeriodoLookup
from apps.mutual.models import DetalleDeclaracionJurada, DetalleMutual, Mutual, Periodo
from selectable.forms import AutoCompleteSelectField, AutoComboboxSelectWidget



class FormDetalle(forms.Form):
    origen = forms.CharField(max_length=100,initial='', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    destino = forms.CharField(max_length=100,initial='', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    concep1 = forms.IntegerField(initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    concep2 = forms.IntegerField(initial=0, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def clean_origen(self):
        origen = self.cleaned_data['origen']
        if origen.strip() == '':
            return "*"
        return origen
    
    def clean_destino(self):
        destino = self.cleaned_data['destino']
        if destino.strip() == '':
            return "*"
        return destino
    
    def conceptoExiste(self, concepto):
        return  DetalleMutual.objects.filter(concepto_1 = concepto).exists() or DetalleMutual.objects.filter(concepto_2 = concepto).exists()
    
        
    def clean_concep1(self):
        concep1 = self.cleaned_data.get('concep1')
       
        if concep1 > 1:
            if self.conceptoExiste(concep1):
                raise forms.ValidationError("El concepto ya existe asociado a otra mutual")
        
        if concep1 is not None and concep1 <= 0:
            raise forms.ValidationError("El valor debe ser mayor que 0.")
        
        return concep1

    def clean_concep2(self):
        # if self.clean_concep1(self) != :
        concep1 = self.cleaned_data.get('concep1')
        concep2 = self.cleaned_data.get('concep2')
        
        if concep2 > 1:
            if self.conceptoExiste(concep2):
                raise forms.ValidationError("El concepto ya existe asociado a otra mutual") 
            
        if concep2 == concep1:
            raise forms.ValidationError("Existen 2 conceptos iguales")
        
        
        if concep2 is not None and concep2 < 0:
            raise forms.ValidationError("El valor debe ser mayor o igual que 0.")
        return concep2

class FormularioMutual(forms.ModelForm):
    class Meta:
        model = Mutual
        fields = '__all__'
        exclude=['estado','detalle','activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Mutual.objects.filter(nombre__iexact = nombre).exists():
          raise forms.ValidationError('Existe una mutual con el mismo nombre')
        else:
          return nombre

    def clean_cuit(self):
        cuit = self.cleaned_data['cuit']
        if len(cuit) != 11 or not cuit.isdigit():
            raise forms.ValidationError('El CUIT debe tener 11 dígitos numéricos.')
    
        if Mutual.objects.filter(cuit__iexact = cuit).exists():
            raise forms.ValidationError('El CUIT ingresado esta vinculado a otra mutual')
        else:
            return cuit
        
from django import forms
from datetime import datetime

class FormularioDJ(forms.ModelForm):
    class Meta:
        model = DetalleDeclaracionJurada
        fields = ['archivo_p', 'archivo_r', 'mes', 'anio']

    archivo_p = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False
    )

    archivo_r = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False
    )

    MES_CHOICES = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]

    mes = forms.ChoiceField(choices=MES_CHOICES, required=False, initial=datetime.now().month,
                            widget=forms.Select(attrs={'class': 'form-select'}))

    ANIO_CHOICES = []
    current_year = datetime.now().year
    for year in range(current_year - 1, current_year + 2):
        ANIO_CHOICES.append((year, str(year)))

    anio = forms.ChoiceField(choices=ANIO_CHOICES, required=False, initial=current_year,
                             widget=forms.Select(attrs={'class': 'form-select'}))

from django.forms import DateInput
from django.utils import timezone

class FormularioPeriodo(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['fecha_inicio']
        widgets = {
            'fecha_inicio': DateInput(attrs={'type': 'date'}),
        }
    
    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        fecha_actual = timezone.now().date()

        if fecha_inicio and fecha_inicio < fecha_actual:
            self.add_error('fecha_inicio', "La fecha debe ser igual o posterior a la fecha actual.")

        return fecha_inicio
    
class MutualFilterForm(forms.Form):
    concepto = forms.IntegerField(label='Concepto', required=False)
    estado = forms.ChoiceField(choices=[('1', 'Todas'), ('2', 'Activas'), ('3', 'Inactivas')], label='Estado', required=False)
    cuit = forms.CharField(label='CUIT', required=False)
    alias = AutoCompleteSelectField(
        lookup_class=MutualLookup,
        required=False,
        widget=AutoComboboxSelectWidget(MutualLookup, attrs={'class': 'form-control'})  # Proporcionar 'lookup_class' y 'attrs'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['concepto'].widget.attrs.update({'placeholder': 'Concepto', 'class': 'form-control'})
        self.fields['estado'].widget.attrs.update({'class': 'form-select'})
        self.fields['cuit'].widget.attrs.update({'placeholder': 'CUIT', 'class': 'form-control'})
        self.fields['alias'].widget.attrs.update({'placeholder': 'Alias'})


class ProfesorFilterForm(forms.Form):
    periodo = AutoCompleteSelectField(
        lookup_class=PeriodoLookup,
        required=False,
        widget=AutoComboboxSelectWidget(PeriodoLookup, attrs={'class': 'form-control', 'placeholder': 'Periodo'})  # Agregar 'placeholder' aquí
    )