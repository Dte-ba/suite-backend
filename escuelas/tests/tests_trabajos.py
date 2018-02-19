# coding: utf-8
import os
from django_rq import get_worker

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from escuelas import models
from escuelas import serializers
from escuelas import fixture
from escuelas import trabajos

get_worker().work(burst=True)

class TrabajosTests(APITestCase):

    def test_puede_llamar_a_un_trabajo_de_forma_normal(self):
        self.assertEqual(models.Trabajo.objects.count(), 0)
        resultado = trabajos.pruebas.sumar(2, 3)
        self.assertEqual(models.Trabajo.objects.count(), 1)
        self.assertEqual(resultado, 5)

    def test_puede_llamar_a_un_trabajo_asincronicamente_y_ver_el_resultado(self):
        self.assertEqual(models.Trabajo.objects.count(), 0)
        trabajos.pruebas.sumar.delay(2, 3)

    def test_puede_listar_trabajos(self):
        response = self.client.get('/api/trabajos')
        self.assertEqual(response.data['cantidad'], 0)

        resultado = trabajos.pruebas.sumar(2, 3)

        response = self.client.get('/api/trabajos')
        self.assertEqual(response.data['cantidad'], 1)

    def test_puede_listar_trabajos(self):
        response = self.client.get('/api/trabajos/sumar?a=1&b=4')
        self.assertTrue(response.data['trabajo_id'])
