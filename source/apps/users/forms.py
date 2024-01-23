from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from ..mutual.models import Mutual

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuario', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RegisterUserMutualForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mutual = forms.ModelChoiceField(queryset=Mutual.objects.all(), required=True, help_text="seleccione la mutual que gestionara")
    
    class Meta:
        model = User  
        fields = UserCreationForm.Meta.fields + ('email',)
        
    def clean_email(self):
        # Validar que el correo electrónico sea único
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso. Por favor, elige otro.")
        return email
