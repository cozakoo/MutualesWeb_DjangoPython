# Generated by Django 4.1.1 on 2024-03-06 10:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0008_alter_rol_tipo'),
        ('administradores', '0002_auto_20240117_1249'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Adminitrador',
            new_name='Administrador',
        ),
    ]
