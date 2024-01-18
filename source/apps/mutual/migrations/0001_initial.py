# Generated by Django 2.2 on 2024-01-18 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DetalleMutual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('R', 'reclamo'), ('P', 'prestamo')], max_length=1)),
                ('origen', models.CharField(max_length=100)),
                ('destino', models.CharField(max_length=100)),
                ('concepto_1', models.IntegerField()),
                ('concepto_2', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Mutual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('cuit', models.BigIntegerField()),
                ('activo', models.BooleanField(default=True)),
                ('detalle', models.ManyToManyField(to='mutual.DetalleMutual')),
            ],
        ),
        migrations.CreateModel(
            name='DeclaracionJurada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('R', 'reclamo'), ('P', 'prestamo')], max_length=1)),
                ('periodo_mes', models.CharField(choices=[('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')], max_length=2)),
                ('archivo_sub', models.FileField(upload_to='documentos/')),
                ('mutual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mutual.Mutual')),
            ],
        ),
    ]
