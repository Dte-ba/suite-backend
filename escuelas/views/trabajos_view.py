# coding: utf-8
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.decorators import list_route

from escuelas.models import Trabajo
from escuelas import trabajos

class TrabajosViewSet(viewsets.ViewSet):

    @authentication_classes([])
    @permission_classes([])
    def list(self, request):
        queryset = Trabajo.objects

        return Response({
            'cantidad': queryset.count(),
            'trabajos': Trabajo.obtener_trabajos_serializados()
        })

    @list_route(methods=['get'])
    def sumar(self, request):
        job = trabajos.pruebas.sumar.delay(2, 2)

        return Response({
            'trabajo_id': job.id
        })
