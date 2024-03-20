from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from mutualWeb.utils.mensajes import mensaje_advertencia
from ..mutual.models import Mutual





class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personaliza los campos si es necesario
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'})


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RegisterUserMutualForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Debe incluir un signo @ en la dirección de correo electrónico.")
    mutual = forms.ModelChoiceField(
        queryset=Mutual.objects.all(),
        required=True,
        help_text="Seleccione la mutual que gestionará",
        widget=forms.Select(attrs={'class': 'form-select'})
    ) 
    
    class Meta:
        model = User  
        fields = UserCreationForm.Meta.fields + ('email',)
    
    
    def clean_username(self):
        
        username = self.cleaned_data.get('username')
        if User.objects.filter(username = username).exists():
            print("existo")
            raise forms.ValidationError("Este nombre de usuario ya esta en uso. Por favor, elige otro.")
        return username    

    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        print("asdasd")
        # Validar que el correo electrónico sea único
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso. Por favor, elige otro.")
        
        # Validar que el correo electrónico incluya un signo @
        if '@' not in email:
            raise forms.ValidationError("El correo electrónico debe incluir un signo @.")
        
        return email



class RegisterUserEmpleadoPublicoForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Debe incluir un signo @ en la dirección de correo electrónico.")
    
    class Meta:
        model = User  
        fields = UserCreationForm.Meta.fields + ('email',)
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        print("asdasd")
        # Validar que el correo electrónico sea único
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso. Por favor, elige otro.")
        
        # Validar que el correo electrónico incluya un signo @
        if '@' not in email:
            raise forms.ValidationError("El correo electrónico debe incluir un signo @.")
        
        return email