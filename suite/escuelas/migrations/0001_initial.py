# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 16:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contacto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('telefono_particular', models.CharField(max_length=100)),
                ('telefono_celular', models.CharField(max_length=100)),
                ('horario', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'db_table': 'contactos',
            },
        ),
        migrations.CreateModel(
            name='Escuela',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cue', models.CharField(db_index=True, max_length=8)),
                ('nombre', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'escuelas',
            },
        ),
        migrations.AddField(
            model_name='contacto',
            name='escuela',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escuelas.Escuela'),
        ),
    ]
