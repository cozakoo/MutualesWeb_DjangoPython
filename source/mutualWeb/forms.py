from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django_select2 import forms as s2forms

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='username', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
