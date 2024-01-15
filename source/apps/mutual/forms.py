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
        exclude=['estado','detalle','activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
       
class FormularioDJ(forms.ModelForm):
    class Meta:
        model = DeclaracionJurada
        fields = '__all__'