# Generated by Django 5.2 on 2025-06-16 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_alter_profile_apellido_alter_profile_nombre_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='fecha_nacimiento',
        ),
        migrations.RemoveField(
            model_name='domiciliario',
            name='fecha_nacimiento',
        ),
    ]
