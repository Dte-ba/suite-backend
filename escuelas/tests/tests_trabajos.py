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

    def test_puede_crear_informe_como_trabajo_no_asincronico(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        perfil_id = self.crear_perfil_con_eventos()

        resultado = trabajos.informes.generar_informe_de_perfil(perfil_id=perfil_id, desde="2017-01-01", hasta="2018-01-01", aplicacion="suite")
        self.assertTrue(resultado.archivo)

    def test_puede_crear_informe_de_robotica_como_trabajo_no_asincronico(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        perfil_id = self.crear_perfil_con_eventos_de_robotica()

        resultado = trabajos.informes.generar_informe_de_perfil(perfil_id=perfil_id, desde="2017-01-01", hasta="2018-01-01", aplicacion="robotica")
        #os.system('open media_archivos_locales/{}'.format(resultado.archivo))
        self.assertTrue(resultado.archivo)

    def test_puede_crear_informe_como_trabajo(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        perfil_id = self.crear_perfil_con_eventos()

        response = self.client.get('/api/trabajos/informe_de_perfil?perfil_id=%d&desde=2017-01-01&hasta=2018-01-01&aplicacion=suite&formato=pdf' %(perfil_id))
        self.assertTrue(response.data['trabajo_id'])

    def crear_perfil_con_eventos(self):
        grupo = Group.objects.create(name="Administrador")

        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.nombre = "Juan"
        user_2.perfil.apellido = "Perez"
        user_2.perfil.cargo = models.Cargo.objects.create(nombre='FED', descripcion="Facilitador Educación Digital")
        user_2.perfil.region = models.Region.objects.create(numero=2)
        user_2.perfil.save()

        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="123", nombre="Escuela 1", localidad=localidad_1)

        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-15", fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-20", fecha_fin="2017-01-20")
        return user_2.perfil.id

    def crear_perfil_con_eventos_de_robotica(self):
        grupo = Group.objects.create(name="Administrador")

        usuario = User.objects.create_user(username='demo', password='123')
        usuario.perfil.group = grupo
        usuario.perfil.nombre = "Juan"
        usuario.perfil.apellido = "Perez"
        usuario.perfil.cargo = models.Cargo.objects.create(nombre='FED', descripcion="Facilitador Educación Digital")
        usuario.perfil.region = models.Region.objects.create(numero=2)
        usuario.perfil.save()

        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito central", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad central", distrito=distrito_1)
        escuela = models.Escuela.objects.create(cue="123", nombre=u"123 en región central", localidad=localidad_1)

        curso = models.CursoDeRobotica.objects.create(nombre="Demo")
        area = models.AreaDeRobotica.objects.create(nombre=u"Troncal")
        taller = models.TallerDeRobotica.objects.create(nombre="Pensamiento Computacional referenciado a la luz y los objetos.", area=area)
        seccion = models.SeccionDeRobotica.objects.create(nombre="prueba")

        evento = models.EventoDeRobotica.objects.create(
            escuela=escuela,
            tallerista=usuario.perfil,
            titulo=taller,
            curso=curso,
            seccion=seccion,
            cantidad_de_alumnos=20,
            area_en_que_se_dicta=area,
            fecha="2017-10-10",
            inicio="10:10:10",
            fin="12:00:01"
        )

        evento_cerrado = models.EventoDeRobotica.objects.create(
            escuela=escuela,
            tallerista=usuario.perfil,
            titulo=taller,
            curso=curso,
            seccion=seccion,
            cantidad_de_alumnos=30,
            area_en_que_se_dicta=area,
            fecha="2017-10-14",
            inicio="12:00:00",
            fin="13:00:00",
            cerrar_evento=True
        )

        return usuario.perfil.id
