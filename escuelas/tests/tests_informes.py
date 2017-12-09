# coding: utf-8
import os
import json
import pprint

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from escuelas import models
from escuelas import serializers
from escuelas import fixture


class InformesTests(APITestCase):

    def test_puede_solicitar_informes_por_fecha(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.nombre = "Juan"
        user_2.perfil.apellido = "Perez"
        user_2.perfil.cargo = models.Cargo.objects.create(nombre='FED', descripcion="Facilitador Educación Digital")
        user_2.perfil.region = models.Region.objects.create(numero=2)
        user_2.perfil.save()

        # Se genera 1 escuela
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="123", nombre="Escuela 1", localidad=localidad_1)

        # Se generan eventos de prueba
        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean dos eventos de prueba. Uno con fecha Enero y otro Marzo
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-15", fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-20", fecha_fin="2017-01-20")

        # Se solicita el informe en modo json sin parámetros, debería retornar un error
        response = self.client.get('/api/informes')
        self.assertEqual(response.data['error'], 'No han especificado todos los argumentos: perfil_id, desde y hasta.')

        # Se solicita el informe en modo json para un perfil en particular
        response = self.client.get('/api/informes?perfil_id=%d&desde=2017-01-01&hasta=2018-01-01' %(user_2.perfil.id))
        self.assertEqual(len(response.data['eventos']), 2)
        self.assertEqual(response.data['perfil']['nombre'], "Juan")
        self.assertEqual(response.data['perfil']['apellido'], "Perez")

        # Se asegura que los eventos llegan en orden, el primero es el mas antiguo.
        self.assertEqual(response.data['eventos'][0]['fecha'], "2017-01-15")
        self.assertEqual(response.data['eventos'][1]['fecha'], "2017-01-20")

        # Si solicita con una fecha inicial posterior al primer evento, tiene que retornar solamente
        # un solo evento (el segundo)
        response = self.client.get('/api/informes?perfil_id=%d&desde=2017-01-18&hasta=2018-01-01' %(user_2.perfil.id))
        self.assertEqual(len(response.data['eventos']), 1)
        self.assertEqual(response.data['eventos'][0]['titulo'], "Evento de prueba de Marzo")

        # Si solicita con un rango de fechas que deja afuera al segundo evento, solo tendría
        # que mostrar el primero de los dos eventos.
        response = self.client.get('/api/informes?perfil_id=%d&desde=2017-01-14&hasta=2017-01-16' %(user_2.perfil.id))
        self.assertEqual(len(response.data['eventos']), 1)
        self.assertEqual(response.data['eventos'][0]['titulo'], "Evento de prueba")

        # Puede perdir el informe en formato html
        response = self.client.get('/api/informes?perfil_id=%d&desde=2017-01-01&hasta=2018-01-01&formato=html' %(user_2.perfil.id))
        self.assertTrue("html" in str(response))
        self.assertFalse("javascript" in str(response))

        # Puede perdir el informe en formato html, con pedido de impresión inmediato
        response = self.client.get('/api/informes?perfil_id=%d&desde=2017-01-01&hasta=2018-01-01&formato=html&imprimir=true' %(user_2.perfil.id))
        self.assertTrue("javascript" in str(response))

        # Puede perdir el informe en formato pdf
        response = self.client.get('/api/informes?perfil_id=%d&desde=2017-01-01&hasta=2018-01-01&formato=pdf' %(user_2.perfil.id))
        self.assertTrue("ReportLab generated PDF document" in str(response))
