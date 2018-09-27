# coding: utf-8
from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from escuelas import models


class EscuelasTestsCase(APITestCase):

    def test_puede_filtrar_escuelas_por_region_y_siembre_viene_600000(self):
        region_2 = models.Region.objects.create(numero=2)
        distrito_1 = models.Distrito.objects.create(nombre="distrito2", region=region_2)
        localidad_1 = models.Localidad.objects.create(nombre="localidad2", distrito=distrito_1)

        # Se construyen 3 escuelas, todas de región 2
        escuela_1 = models.Escuela.objects.create(cue="e1", nombre="Escuela e1 - 600123-e1", localidad=localidad_1)
        escuela_2 = models.Escuela.objects.create(cue="e2", nombre="Escuela e2 - 600123-e2", localidad=localidad_1)
        escuela_3 = models.Escuela.objects.create(cue="e3", nombre="Escuela e3 - 600123-e3", localidad=localidad_1)


        # Se agrega una escuela de región 1, pero que no es 60000000
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito central", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad central", distrito=distrito_1)
        escuela = models.Escuela.objects.create(cue="123", nombre="123 en región central", localidad=localidad_1)


        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        # Si busca una escuela inexistente por criterio de nombre, no retorna nada
        response = self.client.get('/api/escuelas?conformada=false&localidad__distrito__region__numero=2&search=60010239123019230192301293', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 0)

        # Si busca por región 2, tienen que venir las 3 creadas.
        response = self.client.get('/api/escuelas?conformada=false&localidad__distrito__region__numero=2', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 3)

        # Se genera la escuela con cue especial
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito central", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad central", distrito=distrito_1)
        escuela = models.Escuela.objects.create(cue="60000000", nombre="DTE", localidad=localidad_1)

        # Como ahora existe la escuela cue 60000000, tiene que retornarla siempre
        response = self.client.get('/api/escuelas?conformada=false&localidad__distrito__region__numero=2', format='json')
        self.assertEqual(response.data['meta']['pagination']['count'], 4)

    def test_puede_buscar_escuelas_con_muchos_programas_y_no_se_duplican(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        area = models.Area.objects.create(nombre="Urbana")
        modalidad = models.Modalidad.objects.create(nombre="Especial")
        nivel = models.Nivel.objects.create(nombre="Primaria")

        piso_1 = models.Piso.objects.create(servidor="Servidor EXO")
        piso_2 = models.Piso.objects.create(servidor="Servidor EXO")

        tipo_de_financiamiento = models.TipoDeFinanciamiento.objects.create(nombre="Provincial")
        tipo_de_gestion = models.TipoDeGestion.objects.create(nombre="Privada")

        # Se crean los programas
        programa_pad = models.Programa.objects.create(nombre="PAD")
        programa_ci = models.Programa.objects.create(nombre="Conectar Igualdad")


        escuela_1 = models.Escuela.objects.create(
            nombre="escuela 1",
            cue="10000",
            localidad=localidad_1,
            area=area,
            modalidad=modalidad,
            piso=piso_1,
            #tipo_de_financiamiento=tipo_de_financiamiento,
            #tipo_de_gestion=tipo_de_gestion
        )

        escuela_2 = models.Escuela.objects.create(
            nombre="escuela 2",
            cue="20000",
            localidad=localidad_1,
            area=area,
            modalidad=modalidad,
            piso=piso_2,
            #tipo_de_financiamiento=tipo_de_financiamiento,
            #tipo_de_gestion=tipo_de_gestion

        )

        # Vincula los programas a las escuelas.
        escuela_1.programas.add(programa_ci)
        escuela_1.programas.add(programa_pad)

        escuela_2.programas.add(programa_ci)
        escuela_2.programas.add(programa_pad)

        # Hay dos escuelas en la vista inicial.
        response = self.client.get('/api/escuelas')
        self.assertEqual(response.data['meta']['pagination']['count'], 2)

        response = self.client.get('/api/escuelas?conformada=false&query=20000')
        self.assertEqual(response.data['meta']['pagination']['count'], 1)

    def test_puede_editar_escuela(self):
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

        # Se crean dos tipos de financiamiento
        tipo_de_financiamiento_1 = models.TipoDeFinanciamiento.objects.create(nombre="Provincial")
        tipo_de_financiamiento_2 = models.TipoDeFinanciamiento.objects.create(nombre="Municipal")

        #Se crea un tipo de gestión
        tipo_de_gestion = models.TipoDeGestion.objects.create(nombre="Privada")

        #Se crea un programa
        programa = models.Programa.objects.create(nombre="PAD")

        # Inicialmente no hay ninguna escuela
        self.assertEqual(models.Escuela.objects.all().count(), 0)

        # Se crea una escuela
        escuela = models.Escuela.objects.create(
            cue="12345678",
            nombre="Escuela de prueba para edicion",
            localidad=localidad_1,
            area=area,
            modalidad=modalidad,
            nivel=nivel,
            piso=piso,
            tipo_de_gestion=tipo_de_gestion
            )

        escuela.programas.add(programa)
        escuela.tipo_de_financiamiento.add(tipo_de_financiamiento_1)

        # Luego tiene que existir una escuela
        self.assertEqual(models.Escuela.objects.all().count(), 1)

        # Y la api tiene que retornarla
        escuela = models.Escuela.objects.all()[0]
        response = self.client.get('/api/escuelas/{0}'.format(escuela.id))
        self.assertEqual(response.data['cue'], '12345678')
        self.assertEqual(len(response.data['tipo_de_financiamiento']), 1)

        data = {
            "data": {
                "type": "escuelas",
                "id": "1",
                "attributes": {
                    "nombre": "Escuela de prueba editada",
                },
                'relationships': {
                    "tipo-de-financiamiento": {
                        "data": [
                          { "type": "tipos-de-financiamiento", "id": tipo_de_financiamiento_1.id },
                          { "type": "tipos-de-financiamiento", "id": tipo_de_financiamiento_2.id }
                        ]
                      },
                }
            }
        }

        # Luego de hacer el patch ...
        post = self.client.patch('/api/escuelas/{0}'.format(escuela.id), json.dumps(data), content_type='application/vnd.api+json')
        self.assertEqual(post.status_code, 200)

        # La api tiene que devolver 2 tipos de financiamiento
        response = self.client.get('/api/escuelas/{0}'.format(escuela.id))
        self.assertEqual(response.data['cue'], '12345678')
        self.assertEqual(len(response.data['tipo_de_financiamiento']), 2)

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
        tipo_de_financiamiento_1 = models.TipoDeFinanciamiento.objects.create(nombre="Provincial")
        tipo_de_financiamiento_2 = models.TipoDeFinanciamiento.objects.create(nombre="Municipal")

        #Se crea un tipo de gestión
        tipo_de_gestion = models.TipoDeGestion.objects.create(nombre="Privada")

        #Se crea un programa
        programa = models.Programa.objects.create(nombre="PAD")

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
                    "perfil-de-ultima-modificacion": {
                        "data": {
                            "type": "perfiles",
                            "id": user.perfil.id
                        }
                    },
                    "piso": {
                        "data": {
                            "type": "pisos",
                            "id": piso.id
                        }
                    },
                    "tipo_de_financiamiento": {
                        "data": [
                            {
                                "type": "tipos-de-financiamiento",
                                "id": tipo_de_financiamiento_1.id
                            },
                            {
                                "type": "tipos-de-financiamiento",
                                "id": tipo_de_financiamiento_2.id
                            }
                        ]
                    },
                    "tipo_de_gestion": {
                        "data": {
                            "type": "tipos-de-gestion",
                            "id": tipo_de_gestion.id
                        }
                    },
                    "programas": {
                        "data": [{
                            "type": "programas",
                            "id": programa.id
                        }]
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
        self.assertEqual(post.status_code, 201)

        # Luego tiene que haber una escuela
        self.assertEqual(models.Escuela.objects.all().count(), 1)

        # Y la api tiene que retornarla
        escuela = models.Escuela.objects.all()[0]
        response = self.client.get('/api/escuelas/{0}'.format(escuela.id))
        self.assertEqual(response.data['cue'], '88008800')
        self.assertEqual(response.data['nombre'], 'Escuela de Prueba desde el test')
        self.assertEqual(len(response.data['tipo_de_financiamiento']), 2)

    def test_puede_obtener_el_numero_de_region_directamente_desde_la_escuela(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        area = models.Area.objects.create(nombre="Urbana")
        modalidad = models.Modalidad.objects.create(nombre="Especial")
        nivel = models.Nivel.objects.create(nombre="Primaria")

        piso_1 = models.Piso.objects.create(servidor="Servidor EXO")
        piso_2 = models.Piso.objects.create(servidor="Servidor EXO")

        # Se crean los programas
        programa_pad = models.Programa.objects.create(nombre="PAD")
        programa_ci = models.Programa.objects.create(nombre="Conectar Igualdad")


        escuela_1 = models.Escuela.objects.create(
            nombre="escuela 1",
            cue="10000",
            localidad=localidad_1,
            area=area,
            modalidad=modalidad,
            piso=piso_1,
        )

        response = self.client.get('/api/escuelas/{0}'.format(escuela_1.id))
        self.assertEqual(response.data['numero_de_region'], 1)

        escuela_sin_region = models.Escuela.objects.create(
            nombre="escuela sin region",
            cue="20000",
            area=area,
            modalidad=modalidad,
        )

        # Si la escuela no tiene localidad, y no se puede obtener el número
        # de región, se tiene que mostrar un string vacío en lugar de un error.
        response = self.client.get('/api/escuelas/%d' %(escuela_sin_region.id))
        self.assertEqual(response.data['numero_de_region'], '')

    def test_puede_exportar_escuelas(self):
        # Prepara el usuario para chequear contra la api
        user = User.objects.create_user(username='test', password='123')
        self.client.force_authenticate(user=user)

        motivo = models.MotivoDeConformacion.objects.create(nombre="Prueba")
        # Se crean 1 localidad, 1 distrito y 1 región
        region_1 = models.Region.objects.create(numero=1)
        distrito_1 = models.Distrito.objects.create(nombre="distrito1", region=region_1)
        localidad_1 = models.Localidad.objects.create(nombre="localidad1", distrito=distrito_1)
        modalidad_1 = models.Modalidad.objects.create(nombre="Especial")

        # Se generan 3 escuelas
        escuela_1 = models.Escuela.objects.create(nombre=u'San Martín', cue="1", localidad=localidad_1, modalidad=modalidad_1)
        escuela_2 = models.Escuela.objects.create(cue="2", localidad=localidad_1, modalidad=modalidad_1)
        escuela_3 = models.Escuela.objects.create(cue="3", localidad=localidad_1)



        # Inicialmente las 3 escuelas son de primer nivel, se retornan en /api/escuelas
        response = self.client.get('/api/escuelas/export_raw', format='json')
        self.assertEqual(len(response.data['filas']), 3)
        self.assertEqual(response.data['filas'][0][0], u'San Martín' )
        self.assertEqual(response.data['filas'][0][3], 1 )

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
        with self.assertRaises(Exception):
            escuela_1.conformar_con(escuela_3, motivo)

        # Ni una escuela con sigo misma
        with self.assertRaises(Exception):
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
        escuela_4 = models.Escuela.objects.get(id=escuela_4.id)

        self.assertEqual(escuela_4.padre, escuela_1)
        self.assertTrue(escuela_4.motivo_de_conformacion, 'tiene que tener un motivo')
        self.assertTrue(escuela_4.fecha_conformacion, 'tiene que tener una fecha')

        # La escuela 4 se conformó, la api tiene que informarlo
        response = self.client.get('/api/escuelas/{0}'.format(escuela_4.id), format='json')
        self.assertEqual(response.data['conformada'], True)

        # La escuela 1 nunca se conformó
        response = self.client.get('/api/escuelas/{0}'.format(escuela_1.id), format='json')
        self.assertEqual(response.data['conformada'], False)

        self.assertEqual(escuela_1.subescuelas.count(), 3)

        # Y las estadisticas funcionan filtrando conformadas.
        response = self.client.get('/api/escuelas/estadistica', format='json')
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['abiertas'], 1)
        self.assertEqual(response.data['conformadas'], 3)
