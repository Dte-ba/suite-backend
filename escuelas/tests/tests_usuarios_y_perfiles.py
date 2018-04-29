# coding: utf-8
from __future__ import unicode_literals
import os
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
import json
from escuelas import models


class UsuariosYPerfilesTests(APITestCase):


    def test_tiene_depedencias(self):
        result = os.system('convert --version')
        self.assertEqual(result, 0, "Tiene instalado convert en el sistema")

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

    def test_puede_crear_usuario(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        data = {
            "data": {
                "type": "User",
                "attributes": {
                    "username": "usuario1",
                    "password": "asdasd123"
                }
            }
        }

        # Inicialmente solo hay un usuario (el usuario logeado)
        self.assertEqual(User.objects.all().count(), 1)
        # Y tiene que haber un perfil asociado
        self.assertEqual(models.Perfil.objects.all().count(), 1)

        # Luego de hacer el post ...
        post = self.client.post('/api/users/create_user', json.dumps(data), content_type='application/vnd.api+json')

        # ... tiene que haber 2 usuarios ...
        self.assertEqual(User.objects.all().count(), 2)

        # ... y 2 perfiles ...
        self.assertEqual(models.Perfil.objects.all().count(), 2)

        user_2 = models.Perfil.objects.all()[1].user

        # # Y la api tiene que retornar el nuevo usuario
        response = self.client.get('/api/users/{0}'.format(user_2.id))
        self.assertEqual(response.data['username'], 'usuario1')

    def test_puede_crear_persona(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se crean 1 localidad, 1 distrito y 1 región
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)

        data = {
            "data": {
                "type": "perfiles",
                "id": 2,
                "attributes": {
                    "nombre": "Richard",
                    "apellido": "Stallman",
                    "fechadenacimiento": "1953-16-3",
                    "titulo": "",
                    "dni": "11001100",
                    "cuit": "11110011000",
                    "cbu": "09309093090930909309",
                    "email": "stallman@fsf.net",
                    "estado": True,
                    "direccion-calle": "Av. Siempre Libre",
                    "direccion-altura": "10",
                    "direccion-piso": "1",
                    "direccion-depto": "1",
                    "direccion-torre": "B",
                    "codigo-postal": "1010",
                    "telefono-celular": "9090-0011",
                    "telefono-alternativo": "1100-9090",
                    "expediente": "EXP-01100011110",
                    "fecha-de-ingreso": "1985-01-01",
                    "fecha-de-renuncia": "",
                    "email-laboral": "elrichard@abc.gob.ar"
                }
            }
        }
        # print("Data:")
        # pprint.pprint(data)
        #
        # # Inicialmente solo hay un perfil (el usuario logeado)
        # self.assertEqual(models.Perfil.objects.all().count(), 1)
        #
        # # Luego de hacer el post ...
        # post = self.client.post('/api/perfiles', json.dumps(data), content_type='application/vnd.api+json')
        #
        # print("..........")
        # print("Post: ")
        # pprint.pprint(post)
        #
        # # Luego tiene que haber dos perfiles
        # self.assertEqual(models.Perfil.objects.all().count(), 2)
        #
        # # Y la api tiene que retornarla
        # response = self.client.get('/api/perfiles/2')
        # self.assertEqual(response.data['dni'], '11001100')
        # self.assertEqual(response.data['nombre'], 'Richard')
        # self.assertEqual(response.data['apellido'], 'Stallman')
        #
        # pprint.pprint(response)
