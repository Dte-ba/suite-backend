# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-16 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0022_auto_20170609_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='todoElDia',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='evento',
            name='fechafin',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='evento',
            name='fechainicio',
            field=models.DateTimeField(),
        ),
    ]
