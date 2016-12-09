# coding: utf-8
from django.test import TestCase
from rest_framework.test import APITestCase

class APIUsuariosTests(APITestCase):

    def test_ruta_principal_de_la_api(self):
        response = self.client.get('/api/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['users'], "http://testserver/api/users/", "Debería entregar la URL para acceder a usuarios.")

    def test_ruta_users(self):
        response = self.client.get('/api/users', format='json')
        self.assertNotEquals(response, None)

class GeneralesTestCase(TestCase):

    def test_pagina_principal_retorna_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

"""
    def test_index(self):
        response = self.client.get('/customer/index/')
        self.assertEqual(response.status_code, 200)
"""

"""
from django.test import TestCase
from myapp.models import Animal

class AnimalTestCase(TestCase):
    def setUp(self):
        Animal.objects.create(name="lion", sound="roar")
        Animal.objects.create(name="cat", sound="meow")

    def test_animals_can_speak(self):
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')

"""
