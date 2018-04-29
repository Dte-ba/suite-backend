# coding: utf-8
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from escuelas import models, serializers
from escuelas.views import SuitePageNumberPagination, responseError


class PerfilViewSet(viewsets.ModelViewSet):
    queryset = models.Perfil.objects.all()
    resource_name = 'perfiles'
    pagination_class = SuitePageNumberPagination

    serializer_class = serializers.PerfilSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'apellido', 'dni', 'cargo__nombre']
    filter_fields = ['region__numero', "region__id"]

    def create(self, request):
        return Response({})

    def get_queryset(self):
        queryset = self.queryset

        query = self.request.query_params.get('query', None)

        filtro_activos = self.request.query_params.get('activos')

        if filtro_activos:
            filtro = Q(fecha_de_renuncia=None)
            queryset = queryset.filter(filtro)

        if query:
            filtro_nombre = Q(nombre__icontains=query)
            filtro_apellido = Q(apellido__icontains=query)
            filtro_dni = Q(dni__icontains=query)
            filtro_cargo = Q(cargo__nombre__icontains=query)

            queryset = queryset.filter(filtro_nombre | filtro_apellido | filtro_dni | filtro_cargo)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        estadisticas = {
            "total": models.Perfil.objects.all().count(),
            "activos": models.Perfil.objects.filter(fecha_de_renuncia=None).count(),
            "inactivos": models.Perfil.objects.all().exclude(fecha_de_renuncia=None).count(),
            "enDTE": models.Perfil.objects.filter(region__numero=27).exclude(fecha_de_renuncia__isnull=False).count(),
            "enTerritorio": models.Perfil.objects.all().exclude(region__numero=27).exclude(fecha_de_renuncia__isnull=False).count(),
        }
        return Response(estadisticas)

    @detail_route(methods=['get'], url_path='puede-editar-la-accion')
    def puedeEditarLaAccion(self, request, pk=None):
        accion_id = self.request.query_params.get('accion_id', None)
        accion = None

        perfil = self.get_object()

        if not accion_id:
            return responseError("No ha especificado accion_id")

        try:
            accion = models.Evento.objects.get(id=accion_id)
        except models.Evento.DoesNotExist:
            return responseError("No se encuentra el evento id=%d" %(accion_id))

        return Response({
            'puedeEditar': accion.puedeSerEditadaPor(perfil),
            'accion_id': accion_id
        })

    @detail_route(methods=['post'], url_path='definir-clave')
    def definirClave(self, request, **kwargs):
        data = request.data

        if data['clave'] != data['confirmacion']:
            return Response({
                'ok': False,
                'error': 'Las constraseñas no coinciden.'
            })

        if len(data['clave']) < 4:
            return Response({
                'ok': False,
                'error': 'La contraseña es demasiado corta.'
            })

        perfil = self.get_object()
        perfil.user.set_password(data['clave'])
        perfil.user.save()

        return Response({'ok': True})