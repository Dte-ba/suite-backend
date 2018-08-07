# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-08-02 14:27
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escuelas', '0060_perfil_rol_en_robotica'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaDeRobotica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'areasDeRobotica',
                'verbose_name_plural': 'areasDeRobotica',
            },
        ),
        migrations.CreateModel(
            name='CursoDeRobotica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'cursosDeRobotica',
                'verbose_name_plural': 'cursosDeRobotica',
            },
        ),
        migrations.CreateModel(
            name='EventoDeRobotica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_de_alumnos', models.IntegerField(blank=True, default=None, null=True)),
                ('docente_a_cargo', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('fecha', models.DateField(default=datetime.date.today)),
                ('fecha_fin', models.DateField(default=datetime.date.today)),
                ('inicio', models.TimeField(default=datetime.datetime.now)),
                ('fin', models.TimeField(default=datetime.datetime.now)),
                ('minuta', models.TextField(blank=True, default=None, max_length=4096, null=True)),
                ('acta', models.FileField(blank=True, default=None, null=True, upload_to=b'')),
                ('area_en_que_se_dicta', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='area_eventos_de_robotica', to='escuelas.AreaDeRobotica')),
                ('curso', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='curso_eventos_de_robotica', to='escuelas.CursoDeRobotica')),
                ('escuela', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eventos_de_robotica', to='escuelas.Escuela')),
                ('tallerista', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tallerista_eventos_de_robotica', to='escuelas.Perfil')),
            ],
            options={
                'ordering': ('-fecha',),
                'db_table': 'eventos_de_robotica',
                'verbose_name_plural': 'eventos_de_robotica',
            },
        ),
        migrations.CreateModel(
            name='TallerDeRobotica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'talleresDeRobotica',
                'verbose_name_plural': 'talleresDeRobotica',
            },
        ),
        migrations.AddField(
            model_name='eventoderobotica',
            name='titulo',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='titulo_eventos_de_robotica', to='escuelas.TallerDeRobotica'),
        ),
    ]