from django import forms
from apps.mutual.models import Mutual , DeclaracionJurada


class FormDetalle(forms.Form):
    origen = forms.CharField(max_length=100)
    destino = forms.CharField(max_length=100)
    concep1= forms.IntegerField()
    concep2= forms.IntegerField()


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
