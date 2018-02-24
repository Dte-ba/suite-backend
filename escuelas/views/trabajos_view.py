# coding: utf-8
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from django.core.exceptions import ObjectDoesNotExist

from escuelas.models import Trabajo
from escuelas import trabajos

class TrabajosViewSet(viewsets.ViewSet):

    @authentication_classes([])
    @permission_classes([])
    def list(self, request):
        queryset = Trabajo.objects

        return Response(Trabajo.obtener_trabajos_serializados())

    @list_route(methods=['get'])
    def sumar(self, request):
        job = trabajos.pruebas.sumar.delay(2, 2)

        return Response({
            'trabajo_id': job.id
        })

    @list_route(methods=['get'])
    def informe_de_perfil(self, request):
        desde = request.query_params['desde']
        hasta = request.query_params['hasta']
        perfil_id = request.query_params['perfil_id']

        job = trabajos.informes.generar_informe_de_perfil.delay(perfil_id, desde, hasta)

        return Response({
            'trabajo_id': job.id
        })

    @detail_route(methods=['get'])
    def consultar(self, request, pk=None):

        try:
            trabajo = Trabajo.objects.get(trabajo_id=pk)
            url = ""

            if trabajo.archivo:
                url = request.build_absolute_uri(trabajo.archivo.url)

            return Response({
                'id': trabajo.id,
                'progreso': trabajo.progreso,
                'resultado': trabajo.resultado,
                'archivo': url,
                'detalle': trabajo.detalle.split("\n")
            })
        except ObjectDoesNotExist:
            return Response({
                'id': pk,
                'progreso': 0,
                'resultado':  None,
                'archivo': None,
                'detalle': []
            })
