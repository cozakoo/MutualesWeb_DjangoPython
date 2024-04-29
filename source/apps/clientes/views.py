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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from ..clientes.models import Cliente
from ..empleadospublicos.models import EmpleadoPublico







        
        
            