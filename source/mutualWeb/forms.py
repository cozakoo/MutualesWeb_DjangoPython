from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Cuit Mutual', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)