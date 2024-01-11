from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from .models import *
from .forms import *
import random
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import CreateView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():

            # Obtén el nombre de usuario
            # username = form.cleaned_data.get('username')
            codigo_verificacion = str(random.randint(100000, 999999))
            
            print("INICIO DE MENSAJE")
            remitente = "martinarcosvargas2@gmail.com"  # Cambia esto a tu dirección de correo electrónico de Gmail
            contraseña = "nwaetrcbveunziac"
            #Partes del correo
            mensaje = MIMEMultipart()
            mensaje["From"] = remitente
            mensaje["To"] = remitente
            mensaje["Subject"] = "Valida tu cuenta en el Sistema Hospitalario"
            cuerpo_mensaje = f"Tu código de verificación es: {codigo_verificacion}"
            mensaje.attach(MIMEText(cuerpo_mensaje, "plain"))
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(remitente, contraseña)
                server.sendmail(remitente, remitente, mensaje.as_string())
                server.quit()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Usuario {username} creado correctamente. Ahora puedes iniciar sesión.')
                return redirect('dashboard')  # Cambia 'nombre_de_tu_url_de_inicio' con la URL a la que quieres red
            except Exception as e:
                print(f"Error al enviar el correo electrónico: {str(e)}")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registration/registrar_usuario.html', {'form': form})

# Create your views here.
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = FormularioCliente
    template_name = 'cliente_alta.html'
    success_url = reverse_lazy('clientes:confirmacion_cliente')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

def confirmacion_cliente(request):
    return render(request, 'confirmacion_cliente.html')
