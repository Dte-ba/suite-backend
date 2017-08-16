# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from rest_framework.test import APITestCase
import models

class APIUsuariosTests(APITestCase):

    def setUp(self):
        #escuela = models.Escuela.objects.create(nombre="Escuela de ejemplo", cue="123")
        #escuela.save()
        pass

    def test_ruta_principal_de_la_api(self):
        response = self.client.get('/api/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users'], "http://testserver/api/users", "Debería entregar la URL para acceder a usuarios.")

    def test_ruta_users(self):
        response = self.client.get('/api/users', format='json')
        self.assertNotEquals(response, None)

    def test_ruta_escuelas(self):
        response = self.client.get('/api/escuelas', format='json')
        self.assertEquals(response.data['results'], [], "Inicialmente no hay escuelas cargadas")

        # Se genera una escuela de prueba.
        escuela = models.Escuela.objects.create(nombre="Escuela de ejemplo", cue="123")
        escuela.save()

        # ahora la API tiene que exponer una sola escuela.
        response = self.client.get('/api/escuelas', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1, "Tiene que retornarse un solo registro")


class GeneralesTestCase(TestCase):

    def test_pagina_principal_retorna_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_puede_conformar_escuelas(self):
        ## Se generan 3 escuelas
        escuela_1 = models.Escuela.objects.create(cue="1")
        escuela_2 = models.Escuela.objects.create(cue="2")
        escuela_3 = models.Escuela.objects.create(cue="3")

        self.assertEqual(escuela_1, escuela_2)
        self.assertEqual(escuela_1, escuela_3)


class SerializarPermisos(APITestCase):

    def test_puede_serializar_permisos(self):
        # Comienza con un usuario básico
        user = User.objects.create_user(username='test', password='123')

        # Se genera un grupo Cobrador, con dos permisos: cargar pagos y ver informes.
        grupo = Group.objects.create(name='coordinador')

        tipo = ContentType.objects.get(app_label='escuelas', model='evento')

        puede_crear = Permission(name='Puede crear', codename='puede_crear_evento', content_type=tipo)
        puede_crear.save()

        grupo.permissions.add(puede_crear)

        # Se agrega al usuario a ese grupo coordinador
        user.perfil.grupo = grupo

        grupo.save()
        user.save()
        user.perfil.save()

        # En este punto, tiene que existir un perfil de usuario que puede
        # retornar la lista de permisos a traves de la api.
        self.client.login(username='test', password='123')

        # Forzando autenticación porque sin sessionStore de configuración
        # la llamada a self.client.login no guarda la autenticación para las
        # siguientes llamadas.
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/mi-perfil', format='json')

        self.assertEqual(response.data['username'], "test");
        self.assertEqual(len(response.data['permisosComoLista']), 1)
        self.assertEqual(len(response.data['grupos']), 1, "Tiene un solo grupo")
        self.assertEqual(response.data['grupos'][0]['nombre'], 'coordinador', "Tiene asignado el grupo coordinador")


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
