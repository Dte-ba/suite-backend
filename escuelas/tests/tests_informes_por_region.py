# coding: utf-8
import os
import json
import pprint

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

from escuelas import models
from escuelas import trabajos


class InformesPorRegionTests(APITestCase):

    def test_puede_crear_informe_como_trabajo_por_region_no_asincronico(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)
        self.crear_datos_para_los_informes(user)

        resultado = trabajos.informes.generar_informe_de_region(numero_de_region=2, desde="2017-01-01", hasta="2018-01-01", aplicacion="SUITE")
        self.assertTrue(resultado.archivo)

    def crear_datos_para_los_informes(self, user):
        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")
        region_2 = models.Region.objects.create(numero=2)

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.nombre = "Juan"
        user_2.perfil.apellido = "Perez"
        user_2.perfil.cargo = models.Cargo.objects.create(nombre='FED', descripcion="Facilitador Educación Digital")
        user_2.perfil.region = region_2
        user_2.perfil.save()

        user_3 = User.objects.create_user(username='user_3', password='123')
        user_3.perfil.group = grupo
        user_3.perfil.nombre = "Demo"
        user_3.perfil.apellido = "User 3"
        user_3.perfil.cargo = models.Cargo.objects.create(nombre='FED', descripcion="Facilitador Educación Digital")
        user_3.perfil.region = region_2
        user_3.perfil.save()

        # Se genera 1 escuela
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_2)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="123", nombre="Escuela 1", localidad=localidad_1)

        # Se generan eventos de prueba
        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean dos eventos de prueba. Uno con fecha Enero y otro Marzo
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-15", fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-20", fecha_fin="2017-01-20")

        evento_3 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user.perfil, escuela=escuela_1, fecha="2017-01-20", fecha_fin="2017-01-20")
        evento_3.acompaniantes.add(user_2.perfil)
        evento_3.acompaniantes.add(user_3.perfil)
        evento_3.save()
