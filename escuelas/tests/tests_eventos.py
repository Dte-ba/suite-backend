# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

import json

from escuelas import fixture
from escuelas import models


class EventosTestCase(APITestCase):

    def test_puede_pedir_agenda_administrador(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.save()

        escuela_1 = self.crear_escuela_de_region_1()
        escuela_dte = self.crear_escuela_cue_60000000()


        user_2.perfil.region = models.Region.objects.get(numero=1)
        user_2.perfil.save()

        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        evento_1 = models.Evento.objects.create(
            titulo="Evento de prueba",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_1,
            fecha="2017-01-15",
            fecha_fin="2017-01-15")

        evento_2 = models.Evento.objects.create(
            titulo="Evento de prueba de Marzo",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_dte,
            fecha="2017-03-15",
            fecha_fin="2017-03-15")

        # Luego de crear los eventos, ambos deben pertenecer a la region 1
        self.assertEqual(evento_1.region, 1)
        self.assertEqual(evento_2.region, 1)

    def crear_escuela_de_region_1(self):
        # Se genera 1 escuela
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad_1)
        return escuela_1

    def crear_escuela_cue_60000000(self):
        region_27 = models.Region.objects.create(numero=27)
        distrito_27 = models.Distrito.objects.create(nombre="distrito27", region=region_27)
        localidad_27 = models.Localidad.objects.create(nombre="localidad27", distrito=distrito_27)
        escuela_dte = models.Escuela.objects.create(cue="60000000", nombre="DTE", localidad=localidad_27)
        return escuela_dte
