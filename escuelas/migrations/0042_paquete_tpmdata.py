# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-27 14:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0041_paquete_id_devolucion'),
    ]

    operations = [
        migrations.AddField(
            model_name='paquete',
            name='tpmdata',
            field=models.BooleanField(default=False),
        ),
    ]
