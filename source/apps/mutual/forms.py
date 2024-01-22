from django import forms
from apps.mutual.models import Mutual , DeclaracionJurada


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
       
class FormularioDJ(forms.ModelForm):
    class Meta:
        model = DeclaracionJurada
        fields = ['tipo', 'archivos']  # Cambiado de 'archivo' a 'archivos'
