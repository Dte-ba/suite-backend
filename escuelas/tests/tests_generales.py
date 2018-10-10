# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase

import json

from escuelas import fixture
from escuelas import models


class GeneralesTestCase(APITestCase):

    def test_pagina_principal_retorna_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

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
                    "fecha_de_modificacion": "2017-11-09",
                    "cantidad-pedidas": "16",
                    "cantidad-validadas": "",
                    "observaciones": "Probando..."
                },
                "relationships": {
                    "escuela": {
                        "data": {
                            "type": "escuelas",
                            "id": escuela_1.id
                        }
                    },
                    "autor": {
                        "data": {
                            "type": "perfiles",
                            "id": user_2.id
                        }
                    },
                    "estado": {
                        "data": {
                            "type": "estados-de-validacion",
                            "id": estado.id
                        }
                    }
                }
            }
        }



        # Inicialmente no hay ningun paquete
        self.assertEqual(models.Validacion.objects.all().count(), 0)

        # Luego de hacer el post ...
        post = self.client.post('/api/validaciones', json.dumps(data), content_type='application/vnd.api+json')
        self.assertEqual(post.status_code, 201)

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
                            "id": escuela_1.id
                        }
                    },
                    "estado": {
                        "data": {
                            "type": "estados-de-paquete",
                            "id": estado.id
                        }
                    },
                    "perfil-que-solicito-el-paquete": {
                        "data": {
                            "type": "perfiles",
                            "id": user.perfil.id
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

        paquete = models.Paquete.objects.all()[0]

        # Y la api tiene que retornarla
        response = self.client.get('/api/paquetes/{0}'.format(paquete.id))
        self.assertEqual(response.data['fecha_pedido'], '2017-11-09')
        self.assertEqual(response.data['id_hardware'], '240a64647f8c')

    def test_puede_solicitar_muchos_maquetes_de_forma_masiva_a_la_api(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Inicialmente no hay paquetes cargados.
        self.assertEqual(models.Paquete.objects.all().count(), 0)

        estado = models.EstadoDePaquete.objects.create(nombre="Pendiente")
        estado2 = models.EstadoDePaquete.objects.create(nombre="Objetado")
        estado3 = models.EstadoDePaquete.objects.create(nombre="EducAr")

        # Se genera una escuela destino de los paquetes
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        escuela_1 = models.Escuela.objects.create(cue="61480600", nombre="Escuela 1", localidad=localidad_1)

        data_con_errores = """{
            "fecha":"2017-11-09",
            "idPerfil": IDPERFIL,
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
                ["123", "456", "789", "SI"],
                ["aaa123", "dasd", "2222", ""],
                ["ddd", "222", "3333", ""],
                ["", "eee", "", ""],
                ["", "", "", ""],
                ["12345678901234567890", "A12345678901", "123", "no"],
                ["","","", ""]
            ]
        }
        """.replace("IDPERFIL", str(user.perfil.id))


        response = self.client.post('/api/paquetes/importacionMasiva', data_con_errores, content_type='application/x-www-form-urlencoded; charset=UTF-8')


        self.assertTrue(response.data['error'])
        self.assertEquals(response.data['cantidad_de_errores'], 9)



        data_correcta = """{
            "fecha":"2017-11-09",
            "idPerfil": IDPERFIL,
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
                ["12345678901234567890", "A12345678901", "123", "no"],
                ["","","", ""]
            ]
        }
        """.replace("IDPERFIL", str(user.perfil.id))

        response = self.client.post('/api/paquetes/importacionMasiva', data_correcta, content_type='application/x-www-form-urlencoded; charset=UTF-8')

        self.assertEquals(response.data, {'paquetes': 1})
        self.assertEqual(models.Paquete.objects.all().count(), 1)

    def test_puede_exportar_validaciones(self):
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

        # Se crean estados de validacion
        estado_aprobada = models.EstadoDeValidacion.objects.create(nombre="Aprobada")
        estado_objetada = models.EstadoDeValidacion.objects.create(nombre="Objetada")
        estado_pendiente = models.EstadoDeValidacion.objects.create(nombre="Pendiente")

        # Primero no tiene que haber ninguna validación
        self.assertEqual(models.Validacion.objects.all().count(), 0)

        # Se crean 3 validaciones con distinta fecha y distintos estados
        validacion_aprobada = models.Validacion.objects.create(fecha_de_alta="2017-10-01", autor=user_2.perfil, cantidad_pedidas="10", cantidad_validadas="10", observaciones="Prueba", estado=estado_aprobada, escuela=escuela_1)

        validacion_objetada = models.Validacion.objects.create(fecha_de_alta="2017-10-03", autor=user_2.perfil, cantidad_pedidas="100", cantidad_validadas="0", observaciones="Esta no paso", estado=estado_objetada, escuela=escuela_1)

        validacion_pendiente = models.Validacion.objects.create(fecha_de_alta="2017-10-10", autor=user_2.perfil, cantidad_pedidas="120", cantidad_validadas="0", observaciones="Esperando", estado=estado_pendiente, escuela=escuela_1)

        response = self.client.get('/api/validaciones', format='json')

        # Luego tiene que haber 3 validaciones
        self.assertEqual(response.data['meta']['pagination']['count'], 3)

        response = self.client.get('/api/validaciones/export?inicio=2017-10-01&fin=2017-10-02&estado=Aprobada', format='json')

    def test_puede_cambiar_clave_de_perfil(self):
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Se genera un usuario demo
        user_2 = User.objects.create_user(username='demo', password='123')
        user_2.perfil.dni = "123123"
        user_2.perfil.save()

        # Se asegura que la contraseña inicial es 123
        self.assertTrue(user_2.check_password('123'))

        data = {
            "clave": "demo123",
            "confirmacion": "demo123"
        }

        response = self.client.post('/api/perfiles/%d/definir-clave' %(user_2.perfil.id), data)
        self.assertEqual(response.data['ok'], True)


        user_2 = User.objects.get(username='demo')

        # Se asegura que la contraseña cambió a demo123 luego de hacer el post.
        self.assertTrue(user_2.check_password('demo123'))
