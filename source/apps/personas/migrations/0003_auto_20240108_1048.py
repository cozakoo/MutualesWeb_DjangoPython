# Generated by Django 2.2 on 2024-01-08 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0002_persona_confirmar_clave'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='persona',
            name='apellido',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='confirmar_clave',
        ),
        migrations.RemoveField(
            model_name='persona',
            name='nombre',
        ),
    ]
