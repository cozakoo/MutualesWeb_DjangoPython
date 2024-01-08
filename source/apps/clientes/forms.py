from django import forms
from apps.personas.models import Persona
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from utils.regularexpressions import alpha_validator, telefono_validator


class FormularioCliente(forms.ModelForm):
    contraseña = forms.CharField(max_length=50, widget=forms.PasswordInput)
    confirmar_contraseña = forms.CharField(max_length=50, widget=forms.PasswordInput)

    class Meta:
        model = Persona
        fields = '__all__'
        exclude=['es_empleado_publico', 'es_cliente','clave']

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get('contraseña')
        confirmar_contraseña = cleaned_data.get('confirmar_contraseña')

        if contraseña and confirmar_contraseña and contraseña != confirmar_contraseña:
            raise ValidationError('Las contraseñas no coinciden.')

        # Opcional: Puedes cifrar la contraseña antes de guardarla en la base de datos
        cleaned_data['clave'] = make_password(contraseña)
        
        return cleaned_data