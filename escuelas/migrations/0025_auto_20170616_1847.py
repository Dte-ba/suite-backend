# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-16 18:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0024_merge_20170616_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='cbu',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='codigoPosal',
            field=models.CharField(blank=True, default=None, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='direccionAltura',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='direccionCalle',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='direccionDepto',
            field=models.CharField(blank=True, default=None, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='direccionPiso',
            field=models.CharField(blank=True, default=None, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='direccionTorre',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='email',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='localidad',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perfiles', to='escuelas.Localidad'),
        ),
        migrations.AddField(
            model_name='perfil',
            name='titulo',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]