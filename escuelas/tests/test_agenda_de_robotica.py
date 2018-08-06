# coding: utf-8
from __future__ import unicode_literals

from django.contrib.auth.models import User
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
            fecha_fin="2015-10-10",
            inicio="10:10:10",
            fin="12:00:01"
        )

    def test_puede_crear_un_evento_y_obtenerlo_desde_la_api(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        self.crear_evento_de_prueba(user)

        response = self.client.get('/api/eventos-de-robotica', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1)


        fecha = response.data['results'][0]['fecha_formateada']
        self.assertEqual(fecha, "10/10/2017 de 10:10 hs a 12:00 hs")
