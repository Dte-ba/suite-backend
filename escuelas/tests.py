
# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import os
from rest_framework.test import APITestCase
import models
import json
import pprint
import serializers

import fixture

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


class GeneralesTestCase(APITestCase):

    def test_pagina_principal_retorna_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_puede_crear_paquete_de_provision(self):
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

        # Se crea un estado de paquete
        estado = models.EstadoDePaquete.objects.create(nombre="Pendiente")

        # Se crea un pedido de paquete
        paquete_1 = models.Paquete.objects.create(
            escuela=escuela_1,
            fecha_pedido="2017-11-09",
            ne="ee183ce07cfbd86bf819",
            id_hardware="240a64647f8c",
            marca_de_arranque="6",
            estado=estado
        )

        # Se pide la lista de paquetes
        response = self.client.get('/api/paquetes', format='json')

        # Tiene que existir un paquete
        self.assertEqual(models.Paquete.objects.all().count(), 1)

    def test_puede_crear_validacion_desde_api(self):
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

        # Se crea un estado de paquete
        estado = models.EstadoDeValidacion.objects.create(nombre="Pendiente")



        data = {
            "data": {
                "type": "validaciones",
                "id": 1,
                "attributes": {
                    "fecha-de-alta": "2017-11-09",
                    "cantidad-pedidas": "16",
                    "cantidad-validadas": "",
                    "observaciones": "Probando..."
                },
                "relationships": {
                    "escuela": {
                        "data": {
                            "type": "escuelas",
                            "id": 1
                        }
                    },
                    "autor": {
                        "data": {
                            "type": "perfiles",
                            "id": 2
                        }
                    },
                    "estado": {
                        "data": {
                            "type": "estados-de-validacion",
                            "id": 1
                        }
                    }
                }
            }
        }



        # Inicialmente no hay ningun paquete
        self.assertEqual(models.Validacion.objects.all().count(), 0)

        # Luego de hacer el post ...
        post = self.client.post('/api/validaciones', json.dumps(data), content_type='application/vnd.api+json')

        # Luego tiene que haber un evento
        self.assertEqual(models.Validacion.objects.all().count(), 1)

        # Y la api tiene que retornarla
        response = self.client.get('/api/validaciones/1')
        self.assertEqual(response.data['fecha_de_alta'], '2017-11-09')
        self.assertEqual(response.data['cantidad_pedidas'], '16')

    def test_puede_crear_paquete_de_provision_desde_api(self):
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

        # Se crea un estado de paquete
        estado = models.EstadoDePaquete.objects.create(nombre="Pendiente")



        data = {
            "data": {
                "type": "paquetes",
                "id": 1,
                "attributes": {
                    "fecha-pedido": "2017-11-09",
                    "ne": "ee183ce07cfbd86bf819",
                    "id-hardware": "240a64647f8c",
                    "marca-de-arranque": "6",
                    "comentario": "",
                    "carpeta-paquete": "",
                    "fecha-envio": None,
                    "zip-paquete": "",
                    "fecha-devolucion": None,
                    "leido": False
                },
                "relationships": {
                    "escuela": {
                        "data": {
                            "type": "escuelas",
                            "id": 1
                        }
                    },
                    "estado": {
                        "data": {
                            "type": "estados-de-paquete",
                            "id": 1
                        }
                    }
                }
            }
        }



        # Inicialmente no hay ningun paquete
        self.assertEqual(models.Paquete.objects.all().count(), 0)

        # Luego de hacer el post ...
        post = self.client.post('/api/paquetes', json.dumps(data), content_type='application/vnd.api+json')

        # Luego tiene que haber un evento
        self.assertEqual(models.Paquete.objects.all().count(), 1)

        # Y la api tiene que retornarla
        response = self.client.get('/api/paquetes/1')
        self.assertEqual(response.data['fecha_pedido'], '2017-11-09')
        self.assertEqual(response.data['id_hardware'], '240a64647f8c')

    def test_puede_solicitar_muchos_maquetes_de_forma_masiva_a_la_api(self):
        # Inicialmente no hay paquetes cargados.
        self.assertEqual(models.Paquete.objects.all().count(), 0)

        estado = models.EstadoDePaquete.objects.create(nombre="Pendiente")

        # Se genera una escuela destino de los paquetes
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="61480600", nombre="Escuela 1", localidad=localidad_1)

        data = """{
            "fecha":"2017-11-09",
            "escuela": {
                "cue":61480600,
                "nombre":"Eem Nº 14",
                "direccion":"SARCIONE E/ MANCO Y PAZ S/N",
                "telefono":"4268-3084",
                "email":null,
                "latitud":-34.82445078,
                "longitud":-58.34397019,
                "fechaConformacion":null,
                "estado":true,
                "conformada":false,
                "localidad":"122",
                "tipoDeFinanciamiento":null,
                "tipoDeGestion":null,
                "nivel":"3",
                "modalidad":null,
                "area":"1",
                "programas":["1"],
                "piso":"1553",
                "padre":null,
                "motivoDeConformacion":null
            },
            "paquetes":[
                ["123", "456", "789"],
                ["", "", ""],
                ["", "", ""],
                ["", "", ""],
                ["", "", ""],
                ["", "", ""],
                ["","",""]
            ]
        }
        """
        response = self.client.post('/api/paquetes/importacionMasiva', data, content_type='application/x-www-form-urlencoded; charset=UTF-8')
        self.assertEquals(response.data, {'paquetes': 1})

        self.assertEqual(models.Paquete.objects.all().count(), 1)


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

        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil=2&region=1', format='json')

        self.assertEqual(response.data['cantidad'], 1)
        self.assertEqual(len(response.data['eventos']), 1)

    def test_puede_pedir_agenda_coordinador(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un grupo
        grupo = Group.objects.create(name="Coordinador")

        # Se crean dos regiones
        region_1 = models.Region.objects.create(numero=1)
        region_23 = models.Region.objects.create(numero=23)

        # Se crea dos distritos
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        distrito_2 = models.Distrito.objects.create(nombre="distrito2", region=region_23)

        # Se crea una localidad
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        localidad_2 = models.Localidad.objects.create(nombre="localidad2", distrito=distrito_2)

        # Se genera un usuario demo, se asigna una region al perfil
        user_2 = User.objects.create_user(username='demo', password='123')
        perfil_2 = user_2.perfil
        perfil_2.region = region_1
        perfil_2.group = grupo
        perfil_2.save()

        # Se generan 2 escuela y se les asigna distinta localidad
        escuela_1 = models.Escuela.objects.create(cue="1", nombre="escuela 1", localidad=localidad_1)
        escuela_2 = models.Escuela.objects.create(cue="2", nombre="escuela 2", localidad = localidad_2)


        # Se crea una categoria
        categoria_1 = models.CategoriaDeEvento.objects.create(nombre="Categoria 1")

        # Se crean eventos de prueba con fecha de Enero.
        evento_1 = models.Evento.objects.create(
            titulo="Evento de prueba de region 1 y Responsable perfil 2",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_1,
            fecha="2017-01-15",
            fecha_fin="2017-01-15")
        evento_2 = models.Evento.objects.create(
            titulo="Otro evento de prueba de otra escuela, de otra region, de perfil 2",
            categoria=categoria_1,
            responsable=user_2.perfil,
            escuela=escuela_2,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")
        evento_3 = models.Evento.objects.create(
            titulo="Evento de otro perfil, pero de region 1",
            categoria=categoria_1,
            responsable=user.perfil,
            escuela=escuela_1,
            fecha="2017-01-25",
            fecha_fin="2017-01-25")

        # Pide todos (Caso Administrador, Administración y Referente)
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01', format='json')

        self.assertEqual(response.data['cantidad'], 3)

        # Pide solo los de región 1 (Caso Coordinador)
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=1', format='json')

        self.assertEqual(response.data['cantidad'], 2)

        # Pide solo región 23 (Caso Coordinador)
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&region=23', format='json')

        self.assertEqual(response.data['cantidad'], 1)

        # Pide solo perfil 2 (Caso Facilitador ) y Región 1
        response = self.client.get('/api/eventos/agenda?inicio=2017-01-01&fin=2017-02-01&perfil=2&region=1', format='json')

        self.assertEqual(response.data['cantidad'], 1)

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
                            "id": "1"
                        }
                    },
                    "responsable":{
                        "data":{
                            "type": "perfiles",
                            "id": "1"
                        }
                    },
                    "escuela":{
                        "data":{
                            "type":"escuelas",
                            "id":"1"
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
                            "id": 1
                        }
                    },
                    "escuela": {
                        "data": {
                            "type": "escuelas",
                            "id": 1
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
                            "id": 1
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
        response = self.client.get('/api/eventos/1')
        self.assertEqual(response.data['fecha'], '2017-09-06')
        self.assertEqual(response.data['cantidad_de_participantes'], '23')
        self.assertEqual(response.data['requiere_traslado'], True)

        response = self.client.get('/api/eventos/agenda?inicio=2017-08-28&fin=2017-10-07')

        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['categoria'], 'Categoria de Prueba')
        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['region'], 1)
        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['titulo'], 'Evento de prueba desde API')
        self.assertEqual(response.data['eventos'][0]['resumenParaCalendario']['escuela'], 'Nombre demo escuela')


    def test_puede_crear_escuela(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se crean 1 localidad, 1 distrito y 1 región
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)

        # Se crea un area Urbana
        area = models.Area.objects.create(nombre="Urbana")

        # Se crea una modalidad
        modalidad = models.Modalidad.objects.create(nombre="Especial")

        # Se crea un nivel
        nivel = models.Nivel.objects.create(nombre="Primaria")

        # Se crea un piso
        piso = models.Piso.objects.create(servidor="Servidor EXO")

        # Se crea un tipo de financiamiento
        tipo_de_financiamiento = models.TipoDeFinanciamiento.objects.create(nombre="Provincial")

        #Se crea un tipo de gestión
        tipo_de_gestion = models.TipoDeGestion.objects.create(nombre="Privada")

        data = {
            "data": {
                "type": "escuelas",
                "attributes": {
                    "cue": "88008800",
                    "nombre": "Escuela de Prueba desde el test",
                },
                'relationships': {
                    "area": {
                        "data": {
                            "type": "areas",
                            "id": area.id,
                        },
                    },
                    "localidad": {
                        "data": {
                            "type": "localidades",
                            "id": localidad_1.id
                        }
                    },
                    "modalidad": {
                        "data": {
                            "type": "modalidades",
                            "id": modalidad.id
                        }
                    },
                    "nivel": {
                        "data": {
                            "type": "niveles",
                            "id": nivel.id
                        }
                    },
                    #"motivo_de_conformacion": None,
                    #"padre": None,
                    "piso": {
                        "data": {
                            "type": "pisos",
                            "id": piso.id
                        }
                    },
                    "tipo_de_financiamiento": {
                        "data": {
                            "type": "tipos-de-financiamiento",
                            "id": tipo_de_financiamiento.id,
                        }
                    },
                    "tipo_de_gestion": {
                        "data": {
                            "type": "tipos-de-gestion",
                            "id": tipo_de_gestion.id
                        }
                    }
                }
                # "direccion": "",
                # "telefono": "",
                # "email": "",
                # "latitud": "",
                # "longitud": "",
                # "fecha-conformacion": null,
                # "estado": false,
                # "conformada": false
            }
        }

        # Inicialmente no hay ninguna escuela
        self.assertEqual(models.Escuela.objects.all().count(), 0)

        # Luego de hacer el post ...
        post = self.client.post('/api/escuelas', json.dumps(data), content_type='application/vnd.api+json')

        # Luego tiene que haber una escuela
        self.assertEqual(models.Escuela.objects.all().count(), 1)

        # Y la api tiene que retornarla
        response = self.client.get('/api/escuelas/1')
        self.assertEqual(response.data['cue'], '88008800')
        self.assertEqual(response.data['nombre'], 'Escuela de Prueba desde el test')

    def test_puede_conformar_escuelas(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        motivo = models.MotivoDeConformacion.objects.create(nombre="Prueba")

        # Se generan 3 escuelas
        escuela_1 = models.Escuela.objects.create(cue="1")
        escuela_2 = models.Escuela.objects.create(cue="2")
        escuela_3 = models.Escuela.objects.create(cue="3")

        # Inicialmente las 3 escuelas son de primer nivel, se retornan en /api/escuelas
        response = self.client.get('/api/escuelas', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 3)

        # Realizando una conformación. Escuela 1 va a absorver a escuela_2
        escuela_1.conformar_con(escuela_2, motivo)

        # Ahora la api tiene que retornar solo 2 escuelas
        response = self.client.get('/api/escuelas?conformada=false', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 2)

        # Se realiza una conformación más, la 1 absorbe a la 3.
        escuela_1.conformar_con(escuela_3, motivo)
        self.assertEqual(escuela_1.subescuelas.count(), 2)

        self.assertTrue(escuela_3.conformada)

        # Ahora la api tiene que retornar solo 1 escuela
        response = self.client.get('/api/escuelas?conformada=false', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 1)

        # No debería permitirse conformar una escuela más de una vez.
        with self.assertRaises(AssertionError):
            escuela_1.conformar_con(escuela_3, motivo)

        # Ni una escuela con sigo misma
        with self.assertRaises(AssertionError):
            escuela_1.conformar_con(escuela_1, motivo)

        # Ni una escuela que ya se conformó

        """
        # Deshabilitado temporalmente, porque el importador no realiza las
        # conformaciones en orden.

        with self.assertRaises(AssertionError):
            escuela_3.conformar_con(escuela_1, motivo)
        """


        # Por último, la conformación se tiene que poder hacer desde la API
        escuela_4 = models.Escuela.objects.create(cue="4")

        # Inicialmente no está conformada
        self.assertFalse(escuela_4.conformada)

        data = {
            'escuela_que_se_absorbera': escuela_4.id,
            'motivo_id': motivo.id
        }

        response = self.client.post('/api/escuelas/%d/conformar' %(escuela_1.id), data)

        # NOTA: Luego de hacer el request, se tiene que actualizar el objeto
        escuela_4 = models.Escuela.objects.get(id=4)

        self.assertEqual(escuela_4.padre, escuela_1)
        self.assertTrue(escuela_4.motivo_de_conformacion, 'tiene que tener un motivo')
        self.assertTrue(escuela_4.fecha_conformacion, 'tiene que tener una fecha')

        # La escuela 4 se conformó, la api tiene que informarlo
        response = self.client.get('/api/escuelas/4', format='json')
        self.assertEqual(response.data['conformada'], True)

        # La escuela 1 nunca se conformó
        response = self.client.get('/api/escuelas/1', format='json')
        self.assertEqual(response.data['conformada'], False)

        self.assertEqual(escuela_1.subescuelas.count(), 3)

        # Y las estadisticas funcionan filtrando conformadas.
        response = self.client.get('/api/escuelas/estadistica', format='json')
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['abiertas'], 1)
        self.assertEqual(response.data['conformadas'], 3)


class Permisos(APITestCase):

    def test_puede_serializar_permisos(self):
        # Comienza con un usuario básico
        user = User.objects.create_user(username='test', password='123')

        # Se genera un grupo Coordinador, con un permiso
        grupo = Group.objects.create(name='coordinador')

        tipo = ContentType.objects.get(app_label='escuelas', model='evento')

        puede_crear = Permission(name='evento.crear', codename='evento.crear', content_type=tipo)
        puede_crear.save()

        puede_listar = Permission(name='evento.listar', codename='evento.listar', content_type=tipo)
        puede_listar.save()

        puede_administrar = Permission(name='evento.administrar', codename='evento.administrar', content_type=tipo)
        puede_administrar.save()

        # El grupo tiene un solo permiso
        grupo.permissions.add(puede_crear)

        # Se agrega al usuario a ese grupo coordinador
        user.perfil.group = grupo

        # Se asigna una region al perfil de usuario
        region_1 = models.Region.objects.create(numero=1)
        user.perfil.region = region_1

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
        self.assertEqual(len(response.data['grupos']), 1, "Tiene un solo grupo")
        self.assertEqual(response.data['grupos'][0]['nombre'], 'coordinador', "Tiene asignado el grupo coordinador")

        # Hay 3 permisos en el sistema en total
        self.assertEqual(len(response.data['permisos']), 3)

        # Pero esta es la asignación, el usuario de este grupo solo puede crear eventos:
        self.assertEqual(response.data['permisos']['evento.crear'], True);
        self.assertEqual(response.data['permisos']['evento.listar'], False);
        self.assertEqual(response.data['permisos']['evento.administrar'], False);

        response = self.client.get('/api/mi-perfil/1/detalle', format='json')

        # En la vista detalle del grupo ocurre lo mismo, se ven 3 permisos pero este grupo
        # solo puede crear eventos.
        self.assertEqual(response.data['permisos']['evento.crear'], True);
        self.assertEqual(response.data['permisos']['evento.listar'], False);
        self.assertEqual(response.data['permisos']['evento.administrar'], False);

        self.assertEqual(len(response.data['permisosAgrupados']), 1);
        self.assertEqual(response.data['permisosAgrupados'][0]['modulo'], 'evento');
        self.assertEqual(len(response.data['permisosAgrupados'][0]['permisos']), 3);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][0]['accion'], 'crear');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][0]['permiso'], True);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][1]['accion'], 'administrar');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][1]['permiso'], False);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][2]['accion'], 'listar');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][2]['permiso'], False);


    def test_puede_obtener_una_lista_de_todos_los_permisos(self):
        user = User.objects.create_user(username='test', password='123')

        grupo = Group.objects.create(name='coordinador')
        tipo = ContentType.objects.get(app_label='escuelas', model='evento')
        puede_crear_eventos = Permission(name='crear', codename='evento.crear', content_type=tipo)
        puede_crear_eventos.save()

        grupo.permissions.add(puede_crear_eventos)

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/permissions', format='json')

        self.assertEqual(len(response.data['results']), 1)
        item_1 = response.data['results'][0]
        self.assertEquals(item_1["name"], "crear")
        self.assertEquals(item_1["codename"], "evento.crear")
        self.assertEquals(item_1["content_type"], "evento")

    def test_puede_obtener_grupos_junto_con_permisos(self):
        user = User.objects.create_user(username='test', password='123')

        grupo = Group.objects.create(name='coordinador')
        tipo = ContentType.objects.get(app_label='escuelas', model='evento')
        puede_crear_eventos = Permission(name='crear', codename='evento.crear', content_type=tipo)
        puede_crear_eventos.save()

        grupo.permissions.add(puede_crear_eventos)

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/groups', format='json')

        self.assertEqual(len(response.data['results']), 1)
        item_1 = response.data['results'][0]

        self.assertEquals(item_1["name"], "coordinador")

        # Inicialmente este grupo no tiene perfil
        self.assertEquals(item_1["perfiles"], [])

        # Si se vincula el grupo a un perfil ...
        user.perfil.group = grupo
        grupo.save()
        user.save()
        user.perfil.save()

        response = self.client.get('/api/groups', format='json')
        item_1 = response.data['results'][0]

        self.assertEquals(len(item_1["perfiles"]), 1)
        self.assertEquals(item_1["perfiles"][0]['type'], 'perfiles')


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
