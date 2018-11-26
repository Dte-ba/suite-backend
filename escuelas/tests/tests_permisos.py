# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from escuelas import models


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


        # Se asigna una region al perfil de usuario
        region_1 = models.Region.objects.create(numero=1)
        user.perfil.region = region_1

        grupo.save()

        # Se agrega al usuario a ese grupo coordinador
        user.perfil.group = grupo

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
        self.assertEqual(len(response.data['permisos']), 4)

        # Pero esta es la asignación, el usuario de este grupo solo puede crear eventos:
        self.assertEqual(response.data['permisos']['evento.crear'], True);
        self.assertEqual(response.data['permisos']['evento.listar'], False);
        self.assertEqual(response.data['permisos']['evento.administrar'], False);

        response = self.client.get('/api/mi-perfil/{0}/detalle'.format(grupo.id), format='json')

        # En la vista detalle del grupo ocurre lo mismo, se ven 3 permisos pero este grupo
        # solo puede crear eventos.
        self.assertEqual(response.data['permisos']['evento.crear'], True);
        self.assertEqual(response.data['permisos']['evento.listar'], False);
        self.assertEqual(response.data['permisos']['evento.administrar'], False);

        self.assertEqual(len(response.data['permisosAgrupados']), 2);
        self.assertEqual(response.data['permisosAgrupados'][0]['modulo'], 'evento');
        self.assertEqual(len(response.data['permisosAgrupados'][0]['permisos']), 3);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][0]['accion'], 'crear');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][0]['permiso'], True);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][1]['accion'], 'listar');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][1]['permiso'], False);

        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][2]['accion'], 'administrar');
        self.assertEqual(response.data['permisosAgrupados'][0]['permisos'][2]['permiso'], False);

    def test_puede_sustituir_a_otro_usuario(self):
        # Comienza con dos usuarios
        user = User.objects.create_user(username='test', password='123')
        usuario_secundario = User.objects.create_user(username='secundario', password='123')

        # Se genera un grupo para el administrador
        grupo = Group.objects.create(name='coordinador')

        tipo = ContentType.objects.get(app_label='escuelas', model='evento')
        puede_administrar = Permission(name='perfil.global', codename='perfil.global', content_type=tipo)
        puede_administrar.save()
        grupo.permissions.add(puede_administrar)


        # Se asigna una region al perfil de usuario
        region_1 = models.Region.objects.create(numero=1)
        user.perfil.region = region_1
        usuario_secundario.perfil.region = region_1

        grupo.save()

        user.perfil.group = grupo
        user.save()
        user.perfil.save()

        usuario_secundario.perfil.save()
        usuario_secundario.save()

        self.client.login(username='test', password='123')

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/mi-perfil', format='json')

        self.assertEqual(response.data['username'], "test");
        self.assertEqual(len(response.data['grupos']), 1, "Tiene un solo grupo")
        self.assertEqual(response.data['grupos'][0]['nombre'], 'coordinador', "Tiene asignado el grupo coordinador")

        # Accede al perfil de otro usuario correctamente
        response = self.client.get('/api/mi-perfil?perfilInspeccionado=%d' %(usuario_secundario.id), format='json')
        self.assertEqual(response.data['username'], "secundario");

        self.client.logout()

        # Si un usuario que no tiene permisos de administrador intenta ver el perfil de otro usuario falla, por falta de permisos
        self.client.login(username='secundario', password='123')
        self.client.force_authenticate(user=usuario_secundario)
        response = self.client.get('/api/mi-perfil?perfilInspeccionado=%d' %(user.id), format='json')
        self.assertEqual(response.status_code, 500)


    def test_puede_obtener_una_lista_de_todos_los_permisos(self):
        user = User.objects.create_user(username='test', password='123')

        grupo = Group.objects.create(name='coordinador')
        tipo = ContentType.objects.get(app_label='escuelas', model='evento')
        puede_crear_eventos = Permission(name='crear', codename='evento.crear', content_type=tipo)
        puede_crear_eventos.save()

        grupo.permissions.add(puede_crear_eventos)

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/permissions', format='json')

        self.assertEqual(len(response.data['results']), 2)
        item_1 = response.data['results'][1]
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

        self.assertEqual(len(response.data['results']), 2)
        item_1 = response.data['results'][1]

        self.assertEquals(item_1["name"], "coordinador")

        # Inicialmente este grupo no tiene perfil
        self.assertEquals(item_1["perfiles"], [])

        # Si se vincula el grupo a un perfil ...
        user.perfil.group = grupo
        grupo.save()
        user.save()
        user.perfil.save()

        response = self.client.get('/api/groups', format='json')
        item_1 = response.data['results'][1]

        self.assertEquals(len(item_1["perfiles"]), 1)
        self.assertEquals(item_1["perfiles"][0]['type'], 'perfiles')
