# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from escuelas import models


class Filtar(APITestCase):

    def test_puede_filtrar_perfiles(self):
        # Comienza con un usuario básico
        user = User.objects.create_user(username='test', password='123')
        user2 = User.objects.create_user(username='hugo', password='123')

        user.save()
        user.perfil.nombre = "test"
        user.perfil.save()

        user2.save()
        user2.perfil.nombre = "hugo"
        user2.perfil.save()

        # En este punto, tiene que existir un perfil de usuario que puede
        # retornar la lista de permisos a traves de la api.
        self.client.login(username='test', password='123')

        # Forzando autenticación porque sin sessionStore de configuración
        # la llamada a self.client.login no guarda la autenticación para las
        # siguientes llamadas.
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/perfiles', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 2);

        response = self.client.get('/api/perfiles?search=hugo', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1);


    def test_puede_filtrar_tareas(self):
        user = User.objects.create_user(username='test', password='123')
        user.save()
        user.perfil.nombre = "test"
        user.perfil.save()

        self.client.login(username='test', password='123')
        self.client.force_authenticate(user=user)

        # inicialmente no hay tareas
        response = self.client.get('/api/tareas', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 0);

        # Genera los estados de tarea
        estado_abierto = models.EstadoDeTarea.objects.create(nombre="Abierto")
        estado_en_espera = models.EstadoDeTarea.objects.create(nombre="En Espera")

        # Se genera una sola escuela, para la tarea abierta
        region = models.Region.objects.create(numero=1)
        distrito = models.Distrito.objects.create(nombre="distrito1", region=region)
        localidad = models.Localidad.objects.create(nombre="localidad1", distrito=distrito)
        escuela = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad)

        # Genera 3 tareas. Una en estado "abierto" y dos "En espera"
        tarea_1 = models.Tarea.objects.create(titulo="Tarea de ejemplo", estado_de_tarea=estado_abierto, escuela=escuela)
        tarea_2 = models.Tarea.objects.create(titulo="Primer tarea en espera", estado_de_tarea=estado_en_espera)
        tarea_3 = models.Tarea.objects.create(titulo="Segunda tarea en espera", estado_de_tarea=estado_en_espera)

        # Si solicita todas las tareas, tiene que retornar 3
        response = self.client.get('/api/tareas', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 3);

        # Si realiza una búsqueda de "espera", tiene que buscar por título y retornar solo 2.
        response = self.client.get('/api/tareas?search=espera', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 2);

        # Si busca por región, solo tiene que aparecer una tarea (vinculada a la escuela de región 1)
        response = self.client.get('/api/tareas?escuela__localidad__distrito__region__numero=1', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1);

        # Si busca las que están con estado "abierto", tiene que retornar solo 1.
        response = self.client.get('/api/tareas?escuela=%d' %(escuela.id), format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1);