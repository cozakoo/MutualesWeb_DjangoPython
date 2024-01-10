from django import forms
from apps.personas.models import Persona
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from utils.regularexpressions import alpha_validator, telefono_validator

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class RegistroUsuarioForm(UserCreationForm):
    nombre = forms.CharField(max_length=30, required=True, help_text=_("Obligatorio. Máximo 30 caracteres."))
    apellido = forms.CharField(max_length=30, required=True, help_text=_("Obligatorio. Máximo 30 caracteres."))
    telefono = forms.CharField(max_length=15, required=False, help_text=_("Opcional. Máximo 15 caracteres."))
    email = forms.EmailField(max_length=254, required=True, help_text=_("Obligatorio. Se requiere una dirección de correo electrónico válida."))

    username = forms.CharField(max_length=150, help_text=_("Obligatorio. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_."))

    password1 = forms.CharField(
        label=_("Contraseña"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_("Tu contraseña no puede ser demasiado similar a tu otra información personal. Debe contener al menos 8 caracteres. No puede ser una contraseña común. No puede ser completamente numérica."),
    )

    password2 = forms.CharField(
        label=_("Confirmación de contraseña"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Ingresa la misma contraseña que antes, para verificación."),
    )

    class Meta:
        model = User
        fields = ('nombre', 'apellido', 'telefono', 'email', 'username', 'password1', 'password2')

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