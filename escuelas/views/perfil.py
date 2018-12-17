# coding: utf-8
from __future__ import unicode_literals
import base64
import os
import subprocess
import uuid

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_json_api.pagination import PageNumberPagination

from escuelas import models, serializers


class SuitePageNumberPagination(PageNumberPagination):
    max_page_size = 6000


def responseError(mensaje):
    response = Response({
        "error": mensaje
    })

    response.status_code = 500
    return response


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
        filtro_suite = self.request.query_params.get('suite')
        filtro_robotica = self.request.query_params.get('robotica')

        if filtro_activos:
            filtro = Q(fecha_de_renuncia=None)
            queryset = queryset.filter(filtro)
            queryset = queryset.exclude(Q(dni="0000"))

        if query:
            filtro_nombre = Q(nombre__icontains=query)
            filtro_apellido = Q(apellido__icontains=query)
            filtro_dni = Q(dni__icontains=query)
            filtro_cargo = Q(cargo__nombre__icontains=query)

            queryset = queryset.filter(filtro_nombre | filtro_apellido | filtro_dni | filtro_cargo)

        filtro_region = self.request.query_params.get('region')

        if filtro_region:
            filtro = Q(region__numero=filtro_region)
            queryset = queryset.filter(filtro)

        filtro_sort = self.request.query_params.get('sort')

        if filtro_sort:
            queryset = queryset.order_by(filtro_sort)

        if filtro_suite:
            aplicacion_suite = models.Aplicacion.objects.get(nombre=u"SUITE")
            filtro = Q(aplicaciones=aplicacion_suite)
            queryset = queryset.filter(filtro)

        if filtro_robotica:
            aplicacion_robotica = models.Aplicacion.objects.get(nombre=u"Robótica")
            filtro = Q(aplicaciones=aplicacion_robotica)
            queryset = queryset.filter(filtro)


        return queryset

    def perform_update(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_la_foto(serializer)

    def perform_create(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_la_foto(serializer)

    def guardar_modelo_teniendo_en_cuenta_la_foto(self, serializer):
        instancia = serializer.save()
        foto = self.request.data.get('image', None)

        if foto and isinstance(foto, list):
            lista_de_archivos_temporales = []

            nombre = foto[0]['name']
            contenido = foto[0]['contenido']

            archivo_temporal = self.guardar_archivo_temporal(nombre, contenido)
            lista_de_archivos_temporales.append(archivo_temporal)

            prefijo_aleatorio = str(uuid.uuid4())[:12]
            nombre_del_archivo_jpg = '/tmp/%s_archivo.jpg' %(prefijo_aleatorio)

            comando_a_ejecutar = ["convert"] + lista_de_archivos_temporales + ['-compress', 'jpeg', '-quality', '50', '-resize', '1024x1024', nombre_del_archivo_jpg]
            fallo = subprocess.call(comando_a_ejecutar)

            if not fallo:
                from django.core.files import File
                reopen = open(nombre_del_archivo_jpg, "rb")
                django_file = File(reopen)

                instancia.image.save('foto.jpg', django_file, save=False)
            else:
                raise Exception(u"Falló la generación del archivo jpg")

        instancia.save()
        return instancia

    def guardar_archivo_temporal(self, nombre, data):
        if 'data:' in data and ';base64,' in data:
            header, data = data.split(';base64,')

        decoded_file = base64.b64decode(data)
        complete_file_name = str(uuid.uuid4())[:12]+ "_" + nombre
        ruta_completa = os.path.join('/tmp', complete_file_name)

        filehandler = open(ruta_completa, "wb")
        filehandler.write(decoded_file)
        filehandler.close()

        return ruta_completa

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

    @detail_route(methods=['get'], url_path='puede-editar-el-taller')
    def puedeEditarElTaller(self, request, pk=None):
        taller_id = self.request.query_params.get('taller_id', None)
        taller = None

        perfil = self.get_object()

        if not taller_id:
            return responseError("No ha especificado taller_id")

        try:
            taller = models.EventoDeRobotica.objects.get(id=taller_id)
        except models.Evento.DoesNotExist:
            return responseError("No se encuentra el taller id=%d" %(taller_id))

        return Response({
            'puedeEditar': taller.puedeSerEditadaPor(perfil),
            'taller_id': taller_id
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
