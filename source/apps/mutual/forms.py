from django import forms
from apps.mutual.models import Mutual

class FormularioMutual(forms.ModelForm):


    class Meta:
        model = Mutual
        fields = '__all__'
        exclude=['estado','detalle',]
        
       
