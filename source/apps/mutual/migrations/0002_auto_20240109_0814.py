# Generated by Django 2.2 on 2024-01-09 08:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mutual', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mutual',
            old_name='estado',
            new_name='activo',
        ),
    ]
