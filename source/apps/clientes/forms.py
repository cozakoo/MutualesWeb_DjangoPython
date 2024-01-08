from django import forms
from apps.personas.models import Persona

class FormularioCliente(forms.ModelForm):
    confirmar_clave = forms.CharField(max_length=50, widget=forms.PasswordInput)

    class Meta:
        model = Persona
        fields = '__all__'
        exclude=['es_empleado_publico', 'es_cliente']
