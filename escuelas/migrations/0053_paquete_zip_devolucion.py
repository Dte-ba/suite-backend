# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-04-04 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0052_remove_distribuciondepaquete_perfil'),
    ]

    operations = [
        migrations.AddField(
            model_name='paquete',
            name='zip_devolucion',
            field=models.FileField(blank=True, null=True, upload_to=b'devoluciones_de_paquetes/'),
        ),
    ]