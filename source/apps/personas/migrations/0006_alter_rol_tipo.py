# Generated by Django 4.1.1 on 2024-03-06 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0005_alter_persona_id_alter_rol_id_alter_rol_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rol',
            name='tipo',
            field=models.PositiveSmallIntegerField(choices=[(2, 'cliente'), (2, 'administrador'), (3, 'empleadopublico')]),
        ),
    ]
