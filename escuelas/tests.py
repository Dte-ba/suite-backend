# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APITestCase
import models
import pprint

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
        with self.assertRaises(AssertionError):
            escuela_3.conformar_con(escuela_1, motivo)


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
        self.assertTrue(escuela_4.motivoDeConformacion, 'tiene que tener un motivo')
        self.assertTrue(escuela_4.fechaConformacion, 'tiene que tener una fecha')

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
