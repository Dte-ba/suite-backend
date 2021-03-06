# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

import json

from escuelas import fixture
from escuelas import models


class AgendaYEventosTestCase(APITestCase):

    def test_puede_pedir_agenda_administrador(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.save()

        # Se genera 1 escuela
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad_1)

        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean dos eventos de prueba. Uno con fecha Enero y otro Marzo
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-01-15", fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user_2.perfil, escuela=escuela_1, fecha="2017-03-15", fecha_fin="2017-03-15")

        # A estos eventos se les tiene que autogenerar el resumen
        self.assertEqual(evento_1.resumen, '{"categoria": "Categoria 1", "titulo": "Evento de prueba", "region": 1, "responsable": " ", "escuela": "Escuela 1"}')

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil={0}&region=1'.format(user_2.perfil.id), format='json')

        self.assertEqual(response.data['cantidad'], 1)
        self.assertEqual(len(response.data['eventos']), 1)

    def test_puede_consultar_si_un_evento_es_editable(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Administrador")

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.group = grupo
        user_2.perfil.save()

        # Se genera 1 escuela
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad_1)

        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        evento_de_user = models.Evento.objects.create(
            titulo="Evento del usuario user",
            categoria=categoria_1,
            responsable=user.perfil,
            escuela=escuela_1,
            fecha="2017-01-15",
            fecha_fin="2017-01-15"
        )

        evento_de_user2 = models.Evento.objects.create(
            titulo="Evento del usuario user2",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_1,
            fecha="2017-03-15",
            fecha_fin="2017-03-15"
        )

        evento_de_user2_con_user_de_invitado = models.Evento.objects.create(
            titulo="Evento del usuario user2 pero con user de invitado",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_1,
            fecha="2017-03-15",
            fecha_fin="2017-03-15"
        )

        evento_de_user2_con_user_de_invitado.acompaniantes.add(user.perfil)
        evento_de_user2.save()

        # El primer evento lo tiene como responsable a user 1, así que tiene que ser editable por el.
        response = self.client.get('/api/perfiles/%d/puede-editar-la-accion?accion_id=%d' %(user.perfil.id, evento_de_user.id), format='json')
        self.assertEqual(response.data['puedeEditar'], True)

        # El segundo evento no, porque no es responsable ni invitado.
        response = self.client.get('/api/perfiles/%d/puede-editar-la-accion?accion_id=%d' %(user.perfil.id, evento_de_user2.id), format='json')
        self.assertEqual(response.data['puedeEditar'], False)

        # En el tercer evento es invitado, así que debería poder editarlo.
        response = self.client.get('/api/perfiles/%d/puede-editar-la-accion?accion_id=%d' %(user.perfil.id, evento_de_user2_con_user_de_invitado.id), format='json')
        self.assertEqual(response.data['puedeEditar'], True)

    def test_puede_pedir_agenda_coordinador(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Coordinador")

        # Se crean dos regiones
        region_1 = models.Region.objects.create(numero=1)
        region_2 = models.Region.objects.create(numero=2)
        region_3 = models.Region.objects.create(numero=3)

        # Se crea dos distritos
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        distrito_2 = models.Distrito.objects.create(nombre="distrito2", region=region_2)
        distrito_3 = models.Distrito.objects.create(nombre="distrito3", region=region_3)

        # Se crea una localidad
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        localidad_2 = models.Localidad.objects.create(nombre="localidad2", distrito=distrito_2)
        localidad_3 = models.Localidad.objects.create(nombre="localidad3", distrito=distrito_3)

        # Se genera un usuario demo, se asigna una region al perfil
        usuario_1 = User.objects.create_user(username='usuario1', password='123')
        perfil_usuario_1 = usuario_1.perfil
        perfil_usuario_1.apellido = "Apellido de usuario 1"
        perfil_usuario_1.region = region_1
        perfil_usuario_1.group = grupo
        perfil_usuario_1.save()

        # Se genera un usuario demo, se asigna una region al perfil
        usuario_2 = User.objects.create_user(username='usuario2', password='123')
        perfil_usuario_2 = usuario_2.perfil
        perfil_usuario_2.apellido = "Apellido de usuario 2"
        perfil_usuario_2.region = region_2
        perfil_usuario_2.group = grupo
        perfil_usuario_2.save()

        # Se genera un usuario demo, se asigna una region al perfil
        usuario_3 = User.objects.create_user(username='usuario3', password='123')
        perfil_usuario_3 = usuario_3.perfil
        perfil_usuario_3.apellido = "Apellido de usuario 3"
        perfil_usuario_3.region = region_3
        perfil_usuario_3.group = grupo
        perfil_usuario_3.save()

        # Se genera un usuario extra para la región 3
        usuario_extra_3 = User.objects.create_user(username='usuario_extra_3', password='123')
        perfil_usuario_extra_3 = usuario_extra_3.perfil
        perfil_usuario_extra_3.apellido = "Apellido de usuario extra 3"
        perfil_usuario_extra_3.region = region_3
        perfil_usuario_extra_3.group = grupo
        perfil_usuario_extra_3.save()


        # Se generan 2 escuela y se les asigna distinta localidad
        dte = models.Escuela.objects.create(cue="60000000", nombre="DTE", localidad=localidad_1)
        escuela_2 = models.Escuela.objects.create(cue="2", nombre="escuela 2", localidad=localidad_2)
        escuela_3 = models.Escuela.objects.create(cue="3", nombre="escuela 3", localidad=localidad_3)


        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean eventos de prueba con fecha de Enero.
        evento_1 = models.Evento.objects.create(
            titulo=u"Evento de la región 1, del usuario 1",
            categoria=categoria_1,
            responsable=usuario_1.perfil,
            escuela=dte,
            fecha="2017-01-15",
            fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(
            titulo=u"Otro evento de región 1 creado por usuario 2",
            categoria=categoria_1,
            responsable=usuario_2.perfil,
            escuela=dte,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")
        evento_3 = models.Evento.objects.create(
            titulo=u"Evento de región 1 pero con responsable usuario 3",
            categoria=categoria_1,
            responsable=usuario_3.perfil,
            escuela=dte,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")
        evento_4 = models.Evento.objects.create(
            titulo=u"Evento de la escuela 2, del usuario 2",
            categoria=categoria_1,
            responsable=usuario_2.perfil,
            escuela=escuela_2,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")
        evento_5 = models.Evento.objects.create(
            titulo=u"Evento de la región 3, del usuario 3",
            categoria=categoria_1,
            responsable=usuario_3.perfil,
            escuela=escuela_3,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")
        evento_6 = models.Evento.objects.create(
            titulo=u"Evento de la región 3 donde es hay un acompante de la 3",
            categoria=categoria_1,
            responsable=usuario_3.perfil,
            escuela=escuela_3,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")

        evento_6.acompaniantes.add(usuario_extra_3.perfil)
        evento_6.save()

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01', format='json')
        self.assertEqual(response.data['cantidad'], 6)

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=1', format='json')
        self.assertEqual(response.data['cantidad'], 1)

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=2', format='json')
        self.assertEqual(response.data['cantidad'], 2)

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=3', format='json')
        self.assertEqual(response.data['cantidad'], 3)

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil={0}&region={1}'.format(usuario_3.perfil.id, '3'), format='json')
        self.assertEqual(response.data['cantidad'], 3)

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil={0}&region={1}'.format(perfil_usuario_2.id, '2'), format='json')
        self.assertEqual(response.data['cantidad'], 2)

    def test_puede_crear_un_evento_con_acta_desde_la_api(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Coordinador")

        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)

        # Se genera un usuario demo, se asigna una region al perfil
        user_2 = User.objects.create_user(username='demo', password='123')
        perfil_2 = user_2.perfil
        perfil_2.region = region_1
        perfil_2.group = grupo
        perfil_2.save()

        escuela_1 = models.Escuela.objects.create(cue="1", nombre="escuela 1", localidad=localidad_1)
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Intenta agregar un evento con acta

        data = {
            "data":{
                "attributes":{
                    "legacy-id": None,
                    "titulo": "Demo con acta",
                    "fecha": "2017-09-15",
                    "fecha-fin": "2017-09-15",
                    "inicio": "00:00:00",
                    "fin": "02:00:00",
                    "objetivo": "Demo",
                    "minuta": None,
                    "acta-legacy": None,
                    "cantidad-de-participantes": "0",
                    "requiere-traslado": False,
                    "acta": [
                        {
                            "name":"logo3d_en_jpeg.jpg",
                            "contenido": fixture.IMAGEN_1,
                        },
                        {
                            "name":"enjambrebit_logotipo_125x19.png",
                            "contenido": fixture.IMAGEN_2,
                        },
                        {
                            "name":"enjambrebit_isologo_512x379.png",
                            "contenido": fixture.IMAGEN_3,
                        }
                    ],
                    "resumen-para-calendario": None
                },
                "relationships":{
                    "categoria":{
                        "data":{
                            "type": "categorias-de-eventos",
                            "id": categoria_1.id
                        }
                    },
                    "responsable":{
                        "data":{
                            "type": "perfiles",
                            "id": user.perfil.id
                        }
                    },
                    "escuela":{
                        "data":{
                            "type":"escuelas",
                            "id": escuela_1.id
                        }
                    },
                    "acompaniantes":{
                        "data":[

                        ]
                    }
                },
                "type":"eventos"
            }
        }

        response = self.client.post('/api/eventos', json.dumps(data), content_type='application/vnd.api+json')

        response = self.client.get('/api/eventos')
        self.assertTrue(response.data['results'][0]['acta'].startswith('http://testserver/media/'))

        # se borra el archivo generado temporalmente
        #archivo_temporal = response.data['results'][0]['acta'].replace('http://testserver/', '')
        #os.remove(archivo_temporal)

    def test_puede_crear_evento(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se crean 1 localidad, 1 distrito y 1 región
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)

        # Perfil
        perfil = user.perfil

        # Se crea una escuela
        escuela_1 = models.Escuela.objects.create(cue="1", localidad=localidad_1, nombre="Nombre demo escuela")

        # Se crea una categoria de evento
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria de Prueba")

        data = {
            "data": {
                "type": "eventos",
                "id": "28639",
                "attributes": {
                    "titulo": "Evento de prueba desde API",
                    "fecha": "2017-09-06",
                    "fecha-fin": "2017-09-06",
                    "inicio": "09:00:00",
                    "fin": "17:00:00",
                    "objetivo": "Probar que ande el post a la API",
                    "cantidad-de-participantes": 23,
                    "requiere-traslado": True,
                    "resumen-para-calendario": "Sin resumen"
                    # "minuta": null,
                    # "acta-legacy": null,
                    # "legacy-id": null
                },
                "relationships": {
                    "responsable": {
                        "data": {
                            "type": "perfiles",
                            "id": perfil.id
                        }
                    },
                    "escuela": {
                        "data": {
                            "type": "escuelas",
                            "id": escuela_1.id
                        }
                    },
                    "acompaniantes": {
                        "meta": {
                            "count": 0
                        },
                        "data": []
                    },
                    "categoria": {
                        "data": {
                            "type": "categorias-de-eventos",
                            "id": categoria_1.id
                        }
                    }
                }
            }
        }

        # Inicialmente no hay ningun evento
        self.assertEqual(models.Evento.objects.all().count(), 0)

        # Luego de hacer el post ...
        post = self.client.post('/api/eventos', json.dumps(data), content_type='application/vnd.api+json')


        # Luego tiene que haber un evento
        self.assertEqual(models.Evento.objects.all().count(), 1)

        # Y la api tiene que retornarla
        evento = models.Evento.objects.all()[0]
        response = self.client.get('/api/eventos/{0}'.format(evento.id))
        self.assertEqual(response.data['fecha'], '2017-09-06')
        self.assertEqual(response.data['cantidad_de_participantes'], '23')
        self.assertEqual(response.data['requiere_traslado'], True)

        response = self.client.get('/api/eventos/agenda?inicio=2017-08-28&fin=2017-10-07')

        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['categoria'], 'Categoria de Prueba')
        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['region'], 1)
        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['titulo'], 'Evento de prueba desde API')
        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['escuela'], 'Nombre demo escuela')

    def test_puede_obtener_un_listado_de_eventos_de_su_region_y_los_de_60000000(self):
        # Se genera 1 escuela
        region_4 = models.Region.objects.create(numero=4)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_4)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="Escuela 1", localidad=localidad_1)

        # Se genera la escuela central
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_central = models.Escuela.objects.create(cue="60000000", nombre="Escuela 1", localidad=localidad_1)

        # Prepara el usuario de la región 1 para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)
        user.perfil.region = region_4
        user.perfil.save()

        # Prepara un usuario externo
        userExterno = User.objects.create_user(username='testExterno', password='123')
        userExterno.perfil.region = region_1
        userExterno.perfil.save()

        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean dos eventos de prueba. Uno con fecha Enero y otro Marzo
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user.perfil, escuela=escuela_1, fecha="2017-01-15", fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(titulo="Evento de prueba de Marzo", categoria=categoria_1, responsable=user.perfil, escuela=escuela_1, fecha="2017-03-15", fecha_fin="2017-03-15")

        # En su región hay dos eventos
        response = self.client.get('/api/eventos?escuela__localidad__distrito__region__numero=4&perfil={0}'.format(user.perfil.id))
        self.assertEqual(response.data['meta']['pagination']['count'], 2)

        # Si se agregan un evento de región central también lo tiene que ver.
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba", categoria=categoria_1, responsable=user.perfil, escuela=escuela_central, fecha="2017-01-15", fecha_fin="2017-01-15")
        response = self.client.get('/api/eventos?escuela__localidad__distrito__region__numero=4&perfil={0}'.format(user.perfil.id))

        self.assertEqual(response.data['meta']['pagination']['count'], 3)

        # Si se agregan un evento de región central pero no es responsable ni invitado no lo tiene que ver.
        evento_1 = models.Evento.objects.create(titulo="Evento de prueba en donde no es reponsable", responsable=userExterno.perfil, categoria=categoria_1, escuela=escuela_central, fecha="2017-01-15", fecha_fin="2017-01-15")
        response = self.client.get('/api/eventos?escuela__localidad__distrito__region__numero=4&perfil={0}'.format(user.perfil.id))
        self.assertEqual(response.data['meta']['pagination']['count'], 3)

        # Solicitando la agenda tiene que ver los mismos eventos
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2018-01-01&escuela__localidad__distrito__region__numero=4&perfil={0}'.format(user.perfil.id))
        self.assertEqual(len(response.data['eventos']), 3)


        # Solicitando solo los eventos del cue 60000000 debería ver solo uno, porque en el otro no es invitado ni responsable.
        response = self.client.get('/api/eventos?escuela__localidad=&escuela__localidad__distrito=&escuela__localidad__distrito__region__numero=2&page=1&page_size=15&perfil={}&query=60000&responsable__id='.format(user.perfil.id))
        self.assertEqual(response.data['meta']['pagination']['count'], 1)
