# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-11-30 22:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0044_validacion_fecha_de_modificacion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='perfil',
            old_name='codigoPostal',
            new_name='codigo_postal',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='direccionAltura',
            new_name='direccion_altura',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='direccionCalle',
            new_name='direccion_calle',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='direccionDepto',
            new_name='direccion_depto',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='direccionPiso',
            new_name='direccion_piso',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='direccionTorre',
            new_name='direccion_torre',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='emailLaboral',
            new_name='email_laboral',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='fechaDeIngreso',
            new_name='fecha_de_ingreso',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='fechaDeRenuncia',
            new_name='fecha_de_renuncia',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='telefonoAlternativo',
            new_name='telefono_alternativo',
        ),
        migrations.RenameField(
            model_name='perfil',
            old_name='telefonoCelular',
            new_name='telefono_celular',
        ),
    ]
