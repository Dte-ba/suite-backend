# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-09 20:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0016_comentariodevalidacion_legacy_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='cantidadDeParticipantes',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='objetivo',
            field=models.TextField(blank=True, default=None, max_length=4096, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='requiereTraslado',
            field=models.BooleanField(default=False),
        ),
    ]
