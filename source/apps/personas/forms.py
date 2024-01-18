from django import forms
from .models import Persona, Rol

        

class FormularioPersona(forms.ModelForm):
    class Meta:
        model = Persona
        fields = '__all__'
        exclude = ['es_cliente', 'es_admin', 'es_empleado_publico']
        
        
        
