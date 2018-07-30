# coding: utf-8
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from escuelas import models


class MiPerfilViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        if not request.user.is_authenticated():
            return Response({'error': 'El usuario no esta autenticado.'})

        perfilInspeccionado = request.GET.get('perfilInspeccionado')

        if perfilInspeccionado:
            perfil_original = models.Perfil.objects.get(user=request.user)
            perfil = models.Perfil.objects.get(id=perfilInspeccionado)

            # Previene que los usuarios no administradores usen esta característica.
            if not perfil_original.esAdministrador():
                response = Response("No puede sustituir el perfil de otro usuario si no es administrador.")
                response.status_code = 500
                return response
        else:
            perfil = models.Perfil.objects.get(user=request.user)



        data = {
            'username': perfil.user.username,
            'nombre': perfil.nombre,
            'apellido': perfil.apellido,
            'permisos': perfil.obtenerPermisos(),
            'grupos': perfil.obtenerListaDeGrupos(),
            'idPerfil': perfil.id,
            'region': perfil.region.numero,
            'idRegion': perfil.region.id,
            'version': settings.VERSION_NUMBER,
            'tieneAccesoASuite': perfil.aplicaciones.filter(nombre="SUITE").count() > 0,
            'tieneAccesoARobotica': perfil.aplicaciones.filter(nombre="Robótica").count() > 0

        }

        return Response(data)


    @detail_route(methods=['get'])
    def detalle(self, request, pk=None):
        """Emite el detalle completo de un grupo."""
        grupo = Group.objects.get(id=pk)

        permisos_del_grupo = grupo.permissions.all()
        todos_los_permisos = Permission.objects.all()
        permisos_que_no_tiene = set(todos_los_permisos) - set(permisos_del_grupo)

        permisos_como_diccionario = {p.codename: (p in permisos_del_grupo)
                                                for p in todos_los_permisos}

        permisos_agrupados = {}

        for nombre_del_permiso in permisos_como_diccionario:
            modulo, accion = nombre_del_permiso.split('.')
            permiso = permisos_como_diccionario[nombre_del_permiso]

            if modulo not in permisos_agrupados:
                permisos_agrupados[modulo] = []

            permisos_agrupados[modulo].append({'accion': accion, 'permiso': permiso})

        permisos_agrupados_en_lista = [{
                            'modulo': k,
                            'permisos': v,
                            'cantidad': len(v)
                        } for k, v in permisos_agrupados.iteritems()]

        return Response({
            'permisos': permisos_como_diccionario,
            'permisosAgrupados': permisos_agrupados_en_lista,
        })
