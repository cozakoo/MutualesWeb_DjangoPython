# Generated by Django 4.1.1 on 2024-03-22 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mutual', '0017_mutual_alias_alter_mutual_nombre'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mutual',
            name='alias',
            field=models.CharField(max_length=50),
        ),
    ]
