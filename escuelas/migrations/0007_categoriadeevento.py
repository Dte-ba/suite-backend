# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-08-03 13:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0006_auto_20170801_2028'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaDeEvento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'categoriasDeEventos',
                'verbose_name_plural': 'categoriasDeEventos',
            },
        ),
    ]
