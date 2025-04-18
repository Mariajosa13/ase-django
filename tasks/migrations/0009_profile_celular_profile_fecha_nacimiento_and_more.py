# Generated by Django 5.2 on 2025-04-17 19:25

import tasks.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_categoriamascota_productos_destacado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='celular',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, null=True, validators=[tasks.models.validar_mayor_edad]),
        ),
        migrations.AddField(
            model_name='profile',
            name='genero',
            field=models.CharField(blank=True, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro'), ('N', 'Prefiero no decirlo')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='segundo_apellido',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
