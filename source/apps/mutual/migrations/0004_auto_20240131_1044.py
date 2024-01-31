# Generated by Django 2.2 on 2024-01-31 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mutual', '0003_auto_20240131_0844'),
    ]

    operations = [
        migrations.CreateModel(
            name='Periodo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('mes_anio', models.DateField()),
            ],
        ),
        migrations.RemoveField(
            model_name='declaracionjurada',
            name='periodo',
        ),
    ]
