# coding: utf-8
from __future__ import unicode_literals
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from escuelas import models


class AgendaRoboticaTestsCase(APITestCase):

    def crear_evento_de_prueba(self, usuario):
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito central", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad central", distrito=distrito_1)
        escuela = models.Escuela.objects.create(cue="123", nombre="123 en región central", localidad=localidad_1)

        curso = models.CursoDeRobotica.objects.create(nombre="Demo")
        area = models.AreaDeRobotica.objects.create(nombre=u"Troncal")
        taller = models.TallerDeRobotica.objects.create(nombre="Pensamiento Computacional referenciado a la luz y los objetos.", area=area)

        evento = models.EventoDeRobotica.objects.create(
            escuela=escuela,
            tallerista=usuario.perfil,
            titulo=taller,
            curso=curso,
            area_en_que_se_dicta=area,
            fecha="2017-10-10",
            inicio="10:10:10",
            fin="12:00:01"
        )

        default_timezone = timezone.get_default_timezone()
        fecha = datetime(2017, 10, 2, 18, 30, 0)
        evento.fecha_de_creacion = timezone.make_aware(fecha, default_timezone)
        evento.save()

    def test_puede_crear_un_evento_y_obtenerlo_desde_la_api(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        self.crear_evento_de_prueba(user)

        response = self.client.get('/api/eventos-de-robotica', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1)

        fecha = response.data['results'][0]['fecha_formateada']
        self.assertEqual(fecha, "10/10/2017 de 10:10 hs a 12:00 hs")

    def test_puede_listar_y_filtrar_con_limites_incluyentes(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        self.crear_evento_de_prueba(user)

        # Puede filtrar por fecha de creación (prueba 1: rango muy amplio)
        response = self.client.get('/api/eventos-de-robotica?desde_creacion=2017-01-01', format="json")
        self.assertEqual(response.data['meta']['pagination']['count'], 1)

        # Puede filtrar por fecha de creación (prueba 2: evento fuera de rango)
        response = self.client.get('/api/eventos-de-robotica?desde_creacion=2018-01-01&hasta_creacion=2018-02-20', format="json")
        self.assertEqual(response.data['meta']['pagination']['count'], 0)

        # Puede filtrar por fecha de creación (prueba 3: evento con rango corto)
        response = self.client.get('/api/eventos-de-robotica?desde_creacion=2017-09-01&hasta_creacion=2017-11-03', format="json")
        self.assertEqual(response.data['meta']['pagination']['count'], 1)

        # Puede filtrar por fecha de creación (prueba 4: evento con fecha de fin del mismo dia)
        response = self.client.get('/api/eventos-de-robotica?desde_creacion=2017-10-01&hasta_creacion=2017-10-02', format="json")
        self.assertEqual(response.data['meta']['pagination']['count'], 1)
