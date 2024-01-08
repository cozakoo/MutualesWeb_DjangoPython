from django import forms
from apps.personas.models import Persona

class FormularioCliente(forms.ModelForm):
    class Meta:
        model = Persona
        fields = '__all__'
