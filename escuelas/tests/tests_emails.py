# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class Emails(APITestCase):

    def test_puede_enviar_un_mail_a_perfil(self):
        # Comienza con un usuario básico
        user = User.objects.create_user(username='test', password='123')
        user.perfil.email = "hugoruscitti@gmail.com"

        user.save()
        user.perfil.save()

        html = """
            <html>
                <p>Hello, world!</p>
                <p><a href='http://suite.enjambrelab.com.ar/#/login'>Ingresar con llave temporal</a></p>
                <img src='http://suite.enjambrelab.com.ar/imagenes/logo-suite-147033648de4e08c6e5a53d34f8b77dd.png'></img>
            </html>
        """

        #user.perfil.enviar_correo("hola", html)