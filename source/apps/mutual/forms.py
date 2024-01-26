from django import forms
from apps.mutual.models import DetalleDeclaracionJurada, Mutual


class FormDetalle(forms.Form):
    origen = forms.CharField(max_length=100, initial='')
    destino = forms.CharField(max_length=100, initial='')
    concep1 = forms.IntegerField()
    concep2 = forms.IntegerField()

    def clean_concep1(self):
        concep1 = self.cleaned_data.get('concep1')
        if concep1 is not None and concep1 <= 0:
            raise forms.ValidationError("El valor debe ser mayor que 0.")
        return concep1

    def clean_concep2(self):
        concep2 = self.cleaned_data.get('concep2')
        if concep2 is not None and concep2 <= 0:
            raise forms.ValidationError("El valor debe ser mayor que 0.")
        return concep2

class FormularioMutual(forms.ModelForm):
    class Meta:
        model = Mutual
        fields = '__all__'
        exclude=['estado','detalle','activo','']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
    def clean_cuit(self):
        cuit = self.cleaned_data['cuit']
        if len(cuit) != 11 or not cuit.isdigit():
            raise forms.ValidationError('El CUIT debe tener 11 dígitos numéricos.')
        return cuit
       
from django import forms
from datetime import datetime

class FormularioDJ(forms.ModelForm):
    class Meta:
        model = DetalleDeclaracionJurada
        fields = ['archivo_p', 'archivo_r', 'mes', 'anio']

    archivo_p = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=True
    )

    archivo_r = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=True
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