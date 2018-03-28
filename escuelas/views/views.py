# coding: utf-8
from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User, Group, Permission
from django.core.files import File
from django.http import HttpResponse

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

import rest_framework.filters

from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework import status

from escuelas import serializers
from escuelas import models
import base64
import uuid
import os
import datetime
import subprocess
import json

from django.conf import settings
from rest_framework_json_api.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.views.generic import DetailView
from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView
import xlwt
import pprint
import re

import tempfile
import shutil
#
# class LargeResultsSetPagination(pagination.PageNumberPagination):
#     page_size = 1000
#     page_size_query_param = 'page_size'
#     max_page_size = 10000


def home(request):
    return render(request, 'home.html')


def responseError(mensaje):
    response = Response({
        "error": mensaje
    })

    response.status_code = 500
    return response


class SuitePageNumberPagination(PageNumberPagination):
    max_page_size = 6000
    pass

class DemoPDFView(PDFTemplateView):
    template_name = 'hello.html'

    pdf_filename = 'hello.pdf'

    def get_context_data(self, **kwargs):
        return super(DemoPDFView, self).get_context_data(
            pagesize='A4',
            title='Hi there!',
            today=now(),
            **kwargs
        )

class PDFUserDetailView(PDFTemplateResponseMixin, DetailView):
    model = get_user_model()
    template_name = 'user_detail.html'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'])
    def create_user(self, request):
        permission_classes = (AllowAny,)
        serialized = serializers.UserSerializer(data=request.data, context={'request': request})

        if serialized.is_valid():
            usuario = serialized.save()

            resultado = {
                "idPerfil": usuario.perfil.id,
                "idUsuario": usuario.id,
                "data": serialized.data
            }

            return Response(resultado, status=status.HTTP_201_CREATED)
        else:
            values = serialized._errors
            values['errors'] = [{"detail": i[1], "source": {'pointer': i[0]}} for i in values.items()]
            return Response(values, status=status.HTTP_400_BAD_REQUEST)

class EscuelaViewSet(viewsets.ModelViewSet):
    queryset = models.Escuela.objects.all()
    serializer_class = serializers.EscuelaSerializer
    filter_backends = [SearchFilter]
    search_fields = ['cue', 'nombre', 'localidad__distrito__nombre', 'localidad__nombre', 'nivel__nombre', 'programas__nombre']
    #filter_fields = ['localidad__distrito__region__numero', 'conformada']

    def get_queryset(self):
        #solo_padre = Q(padre__isnull=True)
        #queryset = models.Escuela.objects.filter(solo_padre)

        queryset = models.Escuela.objects.all()

        query = self.request.query_params.get('query', None)

        filtro_conformada = self.request.query_params.get('conformada')
        filtro_region = self.request.query_params.get('localidad__distrito__region__numero')
        filtro_programa = self.request.query_params.get('programa')

        if filtro_region:
            filtro = Q(localidad__distrito__region__numero=filtro_region) | Q(cue=60000000)
            queryset = queryset.filter(filtro)

        if filtro_conformada:

            if filtro_conformada.lower() == 'true':
                filtro_conformada = True
            else:
                filtro_conformada = False

            filtro = Q(conformada=filtro_conformada)
            queryset = queryset.filter(filtro)

        if filtro_programa:
            filtro = Q(programas__nombre=filtro_programa)
            queryset = queryset.filter(filtro)


        if query:
            filtro_cue = Q(cue__icontains=query)
            filtro_nombre = Q(nombre__icontains=query)
            filtro_localidad = Q(localidad__nombre__icontains=query)
            filtro_distrito = Q(localidad__distrito__nombre__icontains=query)
            filtro_nivel = Q(nivel__nombre__icontains=query)

            queryset = queryset.filter(filtro_cue | filtro_nombre | filtro_distrito | filtro_localidad | filtro_nivel)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        queryset = models.Escuela.objects.filter(padre__isnull=True)

        estadisticas = {
            "total": queryset.count(),
            "abiertas": queryset.filter(estado=True).count(),
            "cerradas": queryset.filter(estado=False).count(),
            "pisoRoto": queryset.filter(piso__estado=False).count(),
            "pisoFuncionando": queryset.filter(piso__estado=True).count(),
            "conectarIgualdad": queryset.filter(programas__nombre="Conectar Igualdad").count(),
            "pad": queryset.filter(programas__nombre="PAD").count(),
            "responsabilidadEmpresarial": queryset.filter(programas__nombre="Responsabilidad Empresarial").count(),
            "primariaDigital": queryset.filter(programas__nombre="Primaria Digital").count(),
            "escuelasDelFuturo": queryset.filter(programas__nombre="Escuelas del Futuro").count(),
            "conformadas": models.Escuela.objects.filter(padre__isnull=False).count(),
            "validaciones": models.Escuela.objects.filter(validaciones__estado__nombre="Aprobada").count()
        }
        return Response(estadisticas)

    @detail_route(methods=['get'])
    def validaciones(self, request, pk=None):
        escuela = self.get_object()
        filtro = Q(estado__nombre="Aprobada")
        validaciones = escuela.validaciones.filter(filtro)
        # validacion_2017 = escuela.filter(validaciones__estado__nombre="Aprobada")

        estadisticas = {
            "validaciones": validaciones.count()
        }
        return Response(estadisticas)

    @detail_route(methods=['post'])
    def conformar(self, request, pk=None):
        escuela_padre = self.get_object()

        id_escuela = int(request.data['escuela_que_se_absorbera'])
        id_motivo = int(request.data['motivo_id'])

        escuela = models.Escuela.objects.get(id=id_escuela)
        motivo = models.MotivoDeConformacion.objects.get(id=id_motivo)

        escuela_padre.conformar_con(escuela, motivo)

        return Response({'fechaConformacion': escuela.fecha_conformacion})


    def obtener_escuelas_para_exportar(self):
        escuelas = models.Escuela.objects.all()
        filas = []
        for escuela in escuelas:
            #import ipdb; ipdb.set_trace()
            nombre = escuela.nombre
            cue = escuela.cue
            direccion = escuela.direccion
            region = escuela.localidad.distrito.region.numero
            localidad = escuela.localidad.nombre
            distrito = escuela.localidad.distrito.nombre
            if escuela.modalidad :
                modalidad = escuela.modalidad.nombre
            else:
                modalidad = ''
            filas.append([nombre,cue,direccion,region,localidad,distrito,modalidad])
        return filas


    @list_route(methods=['get'])
    def export_raw(self, request):

        return Response({
            'filas': self.obtener_escuelas_para_exportar()
    })

    @list_route(methods=['get'])
    def export(self, request):

        escuelas = self.obtener_escuelas_para_exportar()
        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="escuelas-export.xls"'
        response['Content-Type'] = 'application/vnd.ms-excel'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Escuelas')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        #TODO Definir todos los campos del archivo
        columns = ['Escuela', 'CUE','Dirección','Región', 'Localidad', 'Distrito', 'Modalidad']
        col_num = 6

        # Escribir los headers
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        ws.col(0).width = 256 * 12
        ws.col(1).width = 256 * 12
        font_style = xlwt.XFStyle()

        row_num = 0

        for (indice, fila) in enumerate(escuelas):
            for (indice_columna, columna) in enumerate(fila):
                ws.write(indice+1, indice_columna, columna, font_style)

        wb.save(response)
        return(response)

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = models.Contacto.objects.all()
    serializer_class = serializers.ContactoSerializer


class EventoViewSet(viewsets.ModelViewSet):
    resource_name = 'eventos'
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['escuela__nombre', 'escuela__cue', 'titulo']

    def get_queryset(self):
        queryset = self.queryset
        query = self.request.query_params.get('query', None)

        filtro_region = self.request.query_params.get('escuela__localidad__distrito__region__numero', None)
        filtro_perfil = self.request.query_params.get('perfil', None)


        if filtro_perfil:
            usuario = models.Perfil.objects.get(id=filtro_perfil)
            filtro = Q(responsable=usuario) | Q(acompaniantes=usuario)
            queryset = queryset.filter(filtro)
        else:
            if filtro_region:
                filtro = Q(escuela__localidad__distrito__region__numero=filtro_region)
                queryset = queryset.filter(filtro)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue)

        return queryset.distinct()

    def perform_update(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_el_acta(serializer)

    def perform_create(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_el_acta(serializer)

    def guardar_modelo_teniendo_en_cuenta_el_acta(self, serializer):
        instancia = serializer.save()
        acta = self.request.data.get('acta', None)

        # El acta llega desde el front-end como una lista de diccionarios,
        # donde cada diccionario representa un archivo, con nombre y contenido
        # en base 64.
        if acta and isinstance(acta, list):
            lista_de_archivos_temporales = []

            # Todos los archivos presentes en el front se convierten en archivos
            # físicos reales en /tmp.
            #
            # Este bucle que se encarga de generar todos esos archivos, y guardar
            # en lista_de_archivos_temporales todos los nombres de archivos
            # generados.
            for a in acta:
                nombre = a['name']
                contenido = a['contenido']

                archivo_temporal = self.guardar_archivo_temporal(nombre, contenido)
                lista_de_archivos_temporales.append(archivo_temporal)

            # Con la lista de archivos generados, se invoca a convert para generar
            # el archivo pdf con todas las imágenes.
            prefijo_aleatorio = str(uuid.uuid4())[:12]
            nombre_del_archivo_pdf = '/tmp/%s_archivo.pdf' %(prefijo_aleatorio)

            comando_a_ejecutar = ["convert"] + lista_de_archivos_temporales + ['-compress', 'jpeg', '-quality', '50', '-resize', '1024x1024', nombre_del_archivo_pdf]
            fallo = subprocess.call(comando_a_ejecutar)

            # Con el archivo pdf generado, se intenta cargar el campo 'acta' del
            # modelo django.
            if not fallo:
                from django.core.files import File
                reopen = open(nombre_del_archivo_pdf, "rb")
                django_file = File(reopen)

                instancia.acta.save('acta.pdf', django_file, save=False)
            else:
                raise Exception(u"Falló la generación del archivo pdf")

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
    def informe(self, request):
        start_date = self.request.query_params.get('inicio', None)
        dni = self.request.query_params.get('dni', None)
        end_date = self.request.query_params.get('fin', None)
        filtro_responsable = Q(responsable__dni=dni)

        result = models.Evento.objects.filter(filtro_responsable, fecha__range=(start_date, end_date))
        return Response({})

    @list_route(methods=['get'])
    def agenda(self, request):
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        perfil = self.request.query_params.get('perfil', None)
        region = self.request.query_params.get('region', None)

        eventos = models.Evento.objects.filter(fecha__range=(inicio, fin))

        if region:
            eventos = eventos.filter(Q(escuela__localidad__distrito__region__numero=region) | Q(escuela__cue=60000000))

        if perfil:
            usuario = models.Perfil.objects.get(id=perfil) # El usuario logeado
            eventos = eventos.filter(Q(responsable=usuario) | Q(acompaniantes=usuario)).distinct()
            eventos = eventos[:]
        else:
            if region:
                eventos = [evento for evento in eventos if evento.esDelEquipoRegion(region)]
            else:
                eventos = eventos[:]


        return Response({
                "inicio": inicio,
                "fin": fin,
                "cantidad": len(eventos),
                "eventos": serializers.EventoSerializer(eventos, many=True).data
            })

    @list_route(methods=['get'])
    def agenda_region(self, request):
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        perfil = self.request.query_params.get('perfil', None)

        persona = models.Perfil.objects.get(id=perfil)
        region = persona.region.numero

        eventos = models.Evento.objects.filter( fecha__range=(inicio, fin), escuela__localidad__distrito__region__numero=region, responsable=persona)
        return Response({
                "inicio": inicio,
                "fin": fin,
                "perfil": perfil,
                "persona": persona.apellido,
                "region_del_perfil": persona.region.numero,
                "cantidad": eventos.count(),
                "eventos": serializers.EventoSerializer(eventos, many=True).data,
                "region": region
            })

    @list_route(methods=['get'])
    def estadistica(self, request):
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        perfil = self.request.query_params.get('perfil', None)
        region = self.request.query_params.get('region', None)

        # import ipdb; ipdb.set_trace()

        eventos = models.Evento.objects.filter(fecha__range=(inicio, fin))

        if region:
            eventos = eventos.filter(escuela__localidad__distrito__region__numero=region)

        if perfil:
            usuario = models.Perfil.objects.get(id=perfil) # El usuario logeado
            eventos = eventos.filter(Q(responsable=usuario) | Q(acompaniantes=usuario)).distinct()

        total = eventos.count()
        conActaLegacy = eventos.filter(acta_legacy__gt='').count()
        conActaNueva = eventos.filter(acta__gt='').count()
        conActa = conActaLegacy + conActaNueva
        sinActa = total - conActa

        estadisticas = {
            "total": total,
            "conActa": conActa,
            "sinActa": sinActa,
            "totalOK": models.Evento.objects.all().exclude(escuela__localidad__distrito__region__numero=None).count(),
            "region01": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=1).count(),
            "region02": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=2).count(),
            "region03": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=3).count(),
            "region04": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=4).count(),
            "region05": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=5).count(),
            "region06": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=6).count(),
            "region07": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=7).count(),
            "region08": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=8).count(),
            "region09": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=9).count(),
            "region10": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=10).count(),
            "region11": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=11).count(),
            "region12": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=12).count(),
            "region13": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=13).count(),
            "region14": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=14).count(),
            "region15": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=15).count(),
            "region16": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=16).count(),
            "region17": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=17).count(),
            "region18": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=18).count(),
            "region19": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=19).count(),
            "region20": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=20).count(),
            "region21": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=21).count(),
            "region22": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=22).count(),
            "region23": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=23).count(),
            "region24": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=24).count(),
            "region25": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=25).count(),
            "region27": models.Evento.objects.filter(escuela__localidad__distrito__region__numero=27).count()
        }
        return Response(estadisticas)

    @list_route(methods=['get'])
    def export(self, request):

        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        region = self.request.query_params.get('region', None)

        eventos = models.Evento.objects.filter(fecha__range=(inicio, fin))

        if region:
            eventos = eventos.filter(escuela__localidad__distrito__region__numero=region)

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="acciones-export.xls"'
        response['Content-Type'] = 'application/vnd.ms-excel'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Acciones')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Fecha Inicio', 'Fecha Fin', 'Titulo', 'Región', 'Distrito', 'CUE', 'Responsable', 'Acompañantes', 'Categoria', 'Objetivo', 'Minuta', 'Acta']
        col_num = 2 # 0 y 1 son obligatorias

        # Escribir los headers
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        ws.col(0).width = 256 * 12
        ws.col(1).width = 256 * 12
        ws.col(2).width = 256 * 12
        ws.col(3).width = 256 * 12

        font_style = xlwt.XFStyle()

        row_num = 0

        for accion in eventos:
            fecha = accion.fecha
            fecha_inicio = fecha.strftime("%Y-%m-%d")
            fecha_final = accion.fecha_fin
            fecha_fin = fecha_final.strftime("%Y-%m-%d")
            titulo = accion.titulo
            region = accion.escuela.localidad.distrito.region.numero
            distrito = accion.escuela.localidad.distrito.nombre
            cue = accion.escuela.cue
            responsable = accion.responsable.nombre

            acompaniantes = accion.acompaniantes
            perfiles = ""
            for acompaniante in acompaniantes.all():
                perfiles += acompaniante.nombre + acompaniante.apellido + ", "

            categoria = accion.categoria.nombre
            objetivo = accion.objetivo
            minuta = accion.minuta
            acta = accion.acta
            if acta:
                acta = "Con Acta"
            else:
                acta = ""

            row_num += 1
            ws.write(row_num, 0, fecha_inicio, font_style)
            ws.write(row_num, 1, fecha_fin, font_style)
            ws.write(row_num, 2, titulo, font_style)
            ws.write(row_num, 3, region, font_style)
            ws.write(row_num, 4, distrito, font_style)
            ws.write(row_num, 5, cue, font_style)
            ws.write(row_num, 6, responsable, font_style)
            ws.write(row_num, 7, perfiles, font_style)
            ws.write(row_num, 8, categoria, font_style)
            ws.write(row_num, 9, objetivo, font_style)
            ws.write(row_num, 10, minuta, font_style)
            ws.write(row_num, 11, acta, font_style)

        wb.save(response)
        return(response)

class RegionViewSet(viewsets.ModelViewSet):
    resource_name = 'regiones'
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    #pagination_class = LargeResultsSetPagination

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = models.Perfil.objects.all()
    resource_name = 'perfiles'
    pagination_class = SuitePageNumberPagination

    serializer_class = serializers.PerfilSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'apellido', 'dni', 'cargo__nombre']
    filter_fields = ['region__numero']

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



class MiPerfilViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        if not request.user.is_authenticated():
            return Response({'error': 'El usuario no esta autenticado.'})

        perfil = models.Perfil.objects.get(user=request.user)

        data = {
            'username': request.user.username,
            'nombre': perfil.nombre,
            'apellido': perfil.apellido,
            'permisos': perfil.obtenerPermisos(),
            'grupos': perfil.obtenerListaDeGrupos(),
            'idPerfil': perfil.id,
            'region': perfil.region.numero,
            'idRegion': perfil.region.id,
            'version': settings.VERSION_NUMBER
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

class DistritoViewSet(viewsets.ModelViewSet):
    resource_name = 'distrito'
    queryset = models.Distrito.objects.all()
    serializer_class = serializers.DistritoSerializer
    #pagination_class = LargeResultsSetPagination

class LocalidadViewSet(viewsets.ModelViewSet):
    resource_name = 'localidad'

    queryset = models.Localidad.objects.all()
    serializer_class = serializers.LocalidadSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre']
    filter_fields = ['nombre']

class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = models.Programa.objects.all()
    serializer_class = serializers.ProgramaSerializer

class TipoDeFinanciamientoViewSet(viewsets.ModelViewSet):
    queryset = models.TipoDeFinanciamiento.objects.all()
    serializer_class = serializers.TipoDeFinanciamientoSerializer

class TipoDeGestionViewSet(viewsets.ModelViewSet):
    queryset = models.TipoDeGestion.objects.all()
    serializer_class = serializers.TipoDeGestionSerializer

class AreaViewSet(viewsets.ModelViewSet):
    resource_name = 'area'
    queryset = models.Area.objects.all()
    serializer_class = serializers.AreaSerializer

class NivelViewSet(viewsets.ModelViewSet):
    resource_name = 'nivel'
    queryset = models.Nivel.objects.all()
    serializer_class = serializers.NivelSerializer

class ModalidadViewSet(viewsets.ModelViewSet):
    resource_name = 'modalidad'
    queryset = models.Modalidad.objects.all()
    serializer_class = serializers.ModalidadSerializer

class ExperienciaViewSet(viewsets.ModelViewSet):
    resource_name = 'experiencia'
    queryset = models.Experiencia.objects.all()
    serializer_class = serializers.ExperienciaSerializer

class CargoViewSet(viewsets.ModelViewSet):
    resource_name = 'cargo'
    queryset = models.Cargo.objects.all()
    serializer_class = serializers.CargoSerializer

class ContratoViewSet(viewsets.ModelViewSet):
    resource_name = 'contrato'
    queryset = models.Contrato.objects.all()
    serializer_class = serializers.ContratoSerializer

class PisoViewSet(viewsets.ModelViewSet):
    queryset = models.Piso.objects.all()
    serializer_class = serializers.PisoSerializer

    def perform_update(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_la_llave(serializer)

    def perform_create(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_la_llave(serializer)

    def guardar_modelo_teniendo_en_cuenta_la_llave(self, serializer):
        instancia = serializer.save()
        llave = self.request.data.get('llave', None)

        if llave and isinstance(llave, dict):
            nombre = llave['name']
            contenido = llave['contenido']

            archivo_temporal = self.guardar_archivo_temporal(nombre, contenido)

            reopen = open(archivo_temporal, "rb")
            django_file = File(reopen)

            instancia.llave.save('llave.zip', django_file, save=False)

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


class CargoEscolarViewSet(viewsets.ModelViewSet):
    resource_name = 'cargoEscolar'
    queryset = models.CargoEscolar.objects.all()
    serializer_class = serializers.CargoEscolarSerializer

class ComentarioDeTareaViewSet(viewsets.ModelViewSet):
    resource_name = 'comentario-de-tarea'
    queryset = models.ComentarioDeTarea.objects.all()
    serializer_class = serializers.ComentarioDeTareaSerializer

class MotivoDeTareaViewSet(viewsets.ModelViewSet):
    queryset = models.MotivoDeTarea.objects.all()
    serializer_class = serializers.MotivoDeTareaSerializer

class EstadoDeTareaViewSet(viewsets.ModelViewSet):
    queryset = models.EstadoDeTarea.objects.all()
    serializer_class = serializers.EstadoDeTareaSerializer

class PrioridadDeTareaViewSet(viewsets.ModelViewSet):
    queryset = models.PrioridadDeTarea.objects.all()
    serializer_class = serializers.PrioridadDeTareaSerializer

class TareaViewSet(viewsets.ModelViewSet):
    queryset = models.Tarea.objects.all()
    serializer_class = serializers.TareaSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['autor__nombre', 'autor__apellido', 'titulo']
    filter_fields = ['escuela__localidad__distrito__region__numero', 'escuela', 'estado_de_tarea']


    #
    # def get_queryset(self):
    #
    #     perfil = self.request.query_params.get('perfil', None)
    #     region = self.request.query_params.get('region', None)
    #
    #     usuario = models.Perfil.objects.get(id=perfil) # El usuario logeado
    #     grupo = usuario.group.name
    #
    #     queryset = models.Tarea.objects.all()
    #     query = self.request.query_params.get('query', None)
    #
    #     if query:
    #         filtro_titulo = Q(titulo__icontains=query)
    #         filtro_fechaDeAlta = Q(fecha_de_alta__icontains=query)
    #
    #         queryset = queryset.filter(filtro_titulo | filtro_fechaDeAlta)
    #
    #     return queryset

    @list_route(methods=['get'])
    def lista(self, request):

        perfil = self.request.query_params.get('perfil', None)
        region = self.request.query_params.get('region', None)

        usuario = models.Perfil.objects.get(id=perfil) # El usuario logeado
        grupo = usuario.group.name

        if ((grupo == "Administrador") or (grupo == "Administracion") or (grupo == "Referente")): # Ve todas las tareas de todas las regiones y perfiles
            tareas = models.Tarea.objects.all()
        elif ((grupo == "Coordinador") or (grupo == "Facilitador")): # Ve todas las tareas de todos los perfiles de su región
            tareas = models.Tarea.objects.filter(  escuela__localidad__distrito__region__numero=region)
        else:
            tareas = models.Tarea.objects.filter( escuela__localidad__distrito__region__numero=0, autor=0)

        return Response({
                "perfil": perfil,
                "grupo": grupo,
                "region": region,
                "cantidad": tareas.count(),
                "tareas": serializers.TareaSerializer(tareas, many=True).data

            })


    @list_route(methods=['get'])
    def estadistica(self, request):
        estadisticas = {
            "total": models.Tarea.objects.all().count(),
            "pendientes": models.Tarea.objects.filter(estado_de_tarea__nombre="Abierto").count(),
            "enProgreso": models.Tarea.objects.filter(estado_de_tarea__nombre="En Progreso").count(),
            "prioridadAlta": models.Tarea.objects.filter(prioridad_de_tarea__nombre="Alta").exclude(estado_de_tarea__nombre="Cerrado").count(),
        }
        return Response(estadisticas)

class CategoriaDeEventoViewSet(viewsets.ModelViewSet):
    queryset = models.CategoriaDeEvento.objects.all()
    serializer_class = serializers.CategoriaDeEventoSerializer

class MotivoDeConformacionViewSet(viewsets.ModelViewSet):
    resource_name = 'motivos-de-conformacion'
    queryset = models.MotivoDeConformacion.objects.all()
    serializer_class = serializers.MotivoDeConformacionSerializer

class EstadoDeValidacionViewSet(viewsets.ModelViewSet):
    queryset = models.EstadoDeValidacion.objects.all()
    serializer_class = serializers.EstadoDeValidacionSerializer

class ComentarioDeValidacionViewSet(viewsets.ModelViewSet):
    queryset = models.ComentarioDeValidacion.objects.all()
    serializer_class = serializers.ComentarioDeValidacionSerializer

class ValidacionViewSet(viewsets.ModelViewSet):
    queryset = models.Validacion.objects.all()
    serializer_class = serializers.ValidacionSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['autor__nombre', 'escuela__nombre', 'escuela__cue', 'estado__nombre']
    filter_fields = ['escuela__nombre', 'escuela__localidad__distrito__region__numero']

    def get_queryset(self):
        queryset = models.Validacion.objects.all()
        query = self.request.query_params.get('query', None)

        filtro_eliminada = self.request.query_params.get('eliminada')

        if filtro_eliminada:
            queryset = models.Validacion.objects.all().exclude(estado__nombre="Eliminada")

        if query:
            filtro_autor = Q(autor__nombre__icontains=query)
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)
            filtro_estado = Q(estado__nombre__icontains=query)

            queryset = queryset.filter(filtro_autor | filtro_escuela | filtro_escuela_cue | filtro_estado)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        estadisticas = {
            "total": models.Validacion.objects.all().count(),
            "aprobadas": models.Validacion.objects.filter(estado__nombre="Aprobada").count(),
            "objetadas": models.Validacion.objects.filter(estado__nombre="Objetada").count(),
            "pendientes": models.Validacion.objects.filter(estado__nombre="Pendiente").count(),
        }
        return Response(estadisticas)

    @list_route(methods=['get'])
    def export(self, request):

        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        estadoPedido = self.request.query_params.get('estado', None)

        validaciones = models.Validacion.objects.filter(fecha_de_alta__range=(inicio, fin))

        if estadoPedido != "Todos":
            objeto_estado = models.EstadoDeValidacion.objects.get(nombre=estadoPedido)
            validaciones = validaciones.filter(estado=objeto_estado)

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="validaciones-export.xls"'
        response['Content-Type'] = 'application/vnd.ms-excel'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Validaciones')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Fecha', 'Cantidad Pedidas', 'Cantidad Validadas', 'Pedida por', 'Estado', 'Observaciones', 'Escuela', 'CUE', 'Región', 'Localidad']
        col_num = 2 # 0 y 1 son obligatorias

        # Escribir los headers
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        ws.col(0).width = 256 * 12
        ws.col(1).width = 256 * 12
        ws.col(2).width = 256 * 18
        ws.col(3).width = 256 * 30

        font_style = xlwt.XFStyle()

        row_num = 0

        for validacion in validaciones:
            fecha_de_alta = validacion.fecha_de_alta
            fecha = fecha_de_alta.strftime("%Y-%m-%d")
            cantidad_pedidas = validacion.cantidad_pedidas
            cantidad_validadas = validacion.cantidad_validadas
            autor = validacion.autor.apellido + "," + validacion.autor.nombre
            estado = validacion.estado.nombre
            observaciones = validacion.observaciones
            escuela = validacion.escuela.nombre
            cue = validacion.escuela.cue
            region = validacion.escuela.localidad.distrito.region.numero
            localidad = validacion.escuela.localidad.nombre

            row_num += 1
            ws.write(row_num, 0, fecha, font_style)
            ws.write(row_num, 1, cantidad_pedidas, font_style)
            ws.write(row_num, 2, cantidad_validadas, font_style)
            ws.write(row_num, 3, autor, font_style)
            ws.write(row_num, 4, estado, font_style)
            ws.write(row_num, 5, observaciones, font_style)
            ws.write(row_num, 6, escuela, font_style)
            ws.write(row_num, 7, cue, font_style)
            ws.write(row_num, 8, region, font_style)
            ws.write(row_num, 9, localidad, font_style)

        wb.save(response)
        return(response)

        # return Response({
        #         "inicio": inicio,
        #         "fin": fin,
        #         "cantidad": validaciones.count(),
        #         "validaciones": serializers.ValidacionSerializer(validaciones, many=True).data
        #
        #     })

class EstadoDePaqueteViewSet(viewsets.ModelViewSet):
    queryset = models.EstadoDePaquete.objects.all()
    serializer_class = serializers.EstadoDePaqueteSerializer

class PaqueteViewSet(viewsets.ModelViewSet):
    queryset = models.Paquete.objects.all()
    serializer_class = serializers.PaqueteSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['escuela__nombre', 'escuela__cue', 'estado__nombre', 'id_hardware', 'ne', 'escuela__piso__serie']
    filter_fields = ['escuela__localidad__distrito__region__numero']

    def get_queryset(self):
        queryset = models.Paquete.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)
            filtro_estado = Q(estado__nombre__icontains=query)
            filtro_idHardware = Q(id_hardware__icontains=query)
            filtro_ne = Q(ne__icontains=query)
            filtro_serie = Q(escuela__piso__serie__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue | filtro_estado | filtro_idHardware | filtro_ne | filtro_serie)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):

        # inicio = self.request.query_params.get('inicio', None)
        # fin = self.request.query_params.get('fin', None)
        inicio = "2018-01-01"
        fin = "2018-12-31"

        paquetes = models.Paquete.objects.filter(fecha_pedido__range=(inicio, fin))

        estadisticas = {
            "total": paquetes.count(),
            "pendientes": paquetes.filter(estado__nombre="Pendiente").count(),
            "objetados": paquetes.filter(estado__nombre="Objetado").count(),
            "enviados": paquetes.filter(estado__nombre="EducAr").count(),
            "devueltos": paquetes.filter(estado__nombre="Devuelto").count(),
        }
        return Response(estadisticas)

    @list_route(methods=['get'])
    def export(self, request):

        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        estadoPedido = self.request.query_params.get('estado', None)

        paquetes = models.Paquete.objects.filter(fecha_pedido__range=(inicio, fin))

        if estadoPedido != "Todos":
            objeto_estado = models.EstadoDePaquete.objects.get(nombre=estadoPedido)
            paquetes = paquetes.filter(estado=objeto_estado)

        response = HttpResponse()
        response['Content-Disposition'] = 'attachment; filename="paquetes-export.xls"'
        response['Content-Type'] = 'application/vnd.ms-excel'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Paquetees')

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['CUE', 'Escuela', 'Región', 'Distrito', 'Nro Serie Servidor', 'ID Hardware', 'Marca de Arranque', 'NE', 'Pedido', 'Estado']
        col_num = 2 # 0 y 1 son obligatorias

        # Escribir los headers
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        ws.col(0).width = 256 * 12
        ws.col(1).width = 256 * 12
        ws.col(2).width = 256 * 18
        ws.col(3).width = 256 * 30

        font_style = xlwt.XFStyle()

        row_num = 0

        lista_de_llaves = []

        # directorio_temporal = tempfile.mktemp()
        # directorio_del_archivo_zip = tempfile.mktemp()

        for paquete in paquetes:
            if paquete.escuela:
                cue = paquete.escuela.cue
                escuela = paquete.escuela.nombre
                if paquete.escuela.localidad:
                    region = paquete.escuela.localidad.distrito.region.numero
                    distrito = paquete.escuela.localidad.distrito.nombre
                else:
                    region = "Sin Región"
                    distrito = "Sin Distrito"

                if paquete.escuela.piso:
                    serie_servidor = paquete.escuela.piso.serie
                    if paquete.escuela.piso.llave:
                        llave_servidor = paquete.escuela.piso.llave
                else:
                    serie_servidor = "Sin Servidor"
            else:
                cue = "Sin CUE"
                escuela = "Sin Escuela"
                region = "Sin Región"
                distrito = "Sin Distrito"
                serie_servidor = "Sin Servidor"


            id_hardware = paquete.id_hardware
            marca_de_arranque = paquete.marca_de_arranque
            ne = paquete.ne
            fecha_pedido = paquete.fecha_pedido
            pedido = fecha_pedido.strftime("%Y-%m-%d")
            estado = paquete.estado.nombre


            row_num += 1
            ws.write(row_num, 0, cue, font_style)
            ws.write(row_num, 1, escuela, font_style)
            ws.write(row_num, 2, region, font_style)
            ws.write(row_num, 3, distrito, font_style)
            ws.write(row_num, 4, serie_servidor, font_style)
            ws.write(row_num, 5, id_hardware, font_style)
            ws.write(row_num, 6, marca_de_arranque, font_style)
            ws.write(row_num, 7, ne, font_style)
            ws.write(row_num, 8, pedido, font_style)
            ws.write(row_num, 9, estado, font_style)
            ws.write(row_num, 10, str(llave_servidor), font_style)

            # Si se pidió exportar los paquetes Pendientes, y el estado del paquete era Pendiente, cambiarlo por EducAr
            # Esto es para evitar que al exportar Todos, se actualicen los paquetes.
            # Se guarda la fecha en que se hizo el pedido
            if estadoPedido == "Pendiente":
                if paquete.estado.nombre == "Pendiente":
                    estado_enviado = models.EstadoDePaquete.objects.get(nombre="EducAr")
                    paquete.estado = estado_enviado
                    paquete.fecha_envio = datetime.datetime.now().date()
                    paquete.save()

        # Genera un archivo .zip con todas las llaves
        # nombre_del_archivo_zip = u'llaves'
        # ruta_del_archivo_zip = os.path.join(directorio_del_archivo_zip, nombre_del_archivo_zip)
        # shutil.make_archive(ruta_del_archivo_zip, 'zip', directorio_temporal)

        for llave in lista_de_llaves:
            #### Escribir código que arme el zip con las llaves ###
            print("Agregando " + str(llave) + " al archivo zip")

        wb.save(response)
        return(response)

    def _detectar_errores_en_importacion_masiva_de_paquetes(self, filas):
        """Retorna una lista de errores y evaluaciones sobre las
        filas de importación masiva.

        Si el conjunto de datos no tiene errores, retorna un diccionario
        donde la clave "error" no tendrá valor.
        """
        errores = []
        filas_correctas = 0
        listado_de_id_hardware = []

        for indice, paquete in enumerate(filas):
            ne = unicode(paquete[0])
            id_hardware = unicode(paquete[1])
            marca_de_arranque = unicode(paquete[2])
            tpm_data = unicode(paquete[3])

            if id_hardware in listado_de_id_hardware:
                errores.append(u"Error en la linea %d. Ya hay un pedido con ese ID de Hardware: '%s'. No se puede solicitar mas de uno por ID, aunque tengan distinta marca de arranque." %(indice + 1, id_hardware))

            # chequeamos que no exista un pedido pendiente con los mismos datos
            objeto_estado = models.EstadoDePaquete.objects.get(nombre="Pendiente")
            objeto_paquete = models.Paquete.objects.filter(ne=ne, id_hardware=id_hardware, marca_de_arranque=marca_de_arranque, estado=objeto_estado)

            if objeto_paquete:
                errores.append(u"Error en la linea %d. Ya existe una solicitud de paquete con ese ID de Hardware y esa Marca de arranque." %(indice + 1))

            if not ne and not id_hardware and not marca_de_arranque and not tpm_data:
                continue

            if not re.match(r'^[a-fA-F0-9]{20}$', ne):
                errores.append(u"Error en la linea %d. El campo NE tiene un valor inválido: '%s'. Tiene que ser un valor hexadecimal de 20 dígitos." %(indice + 1, ne))

            if ne == "D581B038CF8F4A8D7670":
                errores.append(u"Error en la linea %d. El campo NE tiene un valor inválido: '%s'. El NE ingresado corresponde al servidor remoto para netbooks 2017 y no puede solicitarse por medio de SUITE." %(indice + 1, ne))

            if not re.match(r'^[a-fA-F0-9]{12}$', id_hardware):
                errores.append(u"Error en la linea %d. El campo ID Hardware tiene un valor inválido: '%s'. Tiene que ser un valor hexadecimal de 12 dígitos." %(indice + 1, id_hardware))

            if not re.match(r'^[a-fA-F0-9]+$', marca_de_arranque):
                errores.append(u"Error en la linea %d. El campo Marca de arranque tiene un valor inválido: '%s'." %(indice + 1, marca_de_arranque))

            if not re.match(r'^si$|^no$|^$', tpm_data, re.IGNORECASE):
                errores.append(u"Error en la linea %d. El campo TPMData tiene un valor inválido: '%s'. Tiene que ser un texto con valor 'si', 'no' o ningún valor." %(indice + 1, tpm_data))

            if tpm_data in ['no', 'NO', 'No'] or tpm_data == "":
                tpm_data = False
            else:
                tpm_data = True
                try:
                    float(marca_de_arranque)
                except ValueError:
                    errores.append(u"Error en la linea %d. Se especificó el uso de TPMData pero la marca de arranque ingresada es hexadecimal." %(indice + 1))

            filas_correctas += 1
            listado_de_id_hardware.append(id_hardware)


        if filas_correctas < 1:
            errores.append("No ha especificado ninguna fila.")

        if errores:
            return {
                'error': u"La importación ha fallado",
                'errores': errores,
                'cantidad_de_errores': len(errores)
            }
        else:
            return {
                'error': False,
                'errores': [],
                'cantidad_de_errores': 0
            }

    @list_route(methods=['post'])
    def importacionMasiva(self, request, **kwargs):
        # TODO: evitar esta conversión, debería llegar el dicionario de datos
        # directamente. Ver si el problema está en la forma de declarar el
        # post el frontend.
        data = json.loads(request.data.keys()[0])

        # Captura los datos del requests, fecha, escuela y lista de paquetes
        # desde la grilla de handsontable.js
        escuela = data['escuela']
        paquetes = data['paquetes']
        fecha = data['fecha']

        # Se obtienen los modelos a relacionar con cada paquete solicitado.
        escuela = models.Escuela.objects.get(cue=escuela['cue'])
        estadoPendiente = models.EstadoDePaquete.objects.get(nombre="Pendiente")

        cantidad_de_paquetes_creados = 0

        validacion = self._detectar_errores_en_importacion_masiva_de_paquetes(paquetes)

        if validacion['error']:
            return Response({
                'error': validacion['error'],
                'errores': validacion['errores'],
                'cantidad_de_errores': len(validacion['errores'])
            })
        else:

            for p in paquetes:
                ne = p[0]
                id_hardware = p[1]
                marca_de_arranque = p[2]
                tpmdata = p[3]

                if tpmdata in ['no', 'NO', 'No'] or tpmdata == "":
                    tpmdata = False
                    # El valor de marca_de_arranque es hexadecimal
                    ma_hexa = marca_de_arranque
                else:
                    tpmdata = True
                    # El valor de marca_de_arranque es decimal, lo convertimos a hexa
                    try: # Si es decimal, no puede contener letras, debe ser un número
                        float(marca_de_arranque)
                        ma_hexa = hex(int(marca_de_arranque))[2:]
                    except ValueError:
                        pass

                # si la linea de handsontable define las tres columnas, se intenta
                # generar un paquete con esos datos
                if ne and id_hardware and marca_de_arranque:
                    models.Paquete.objects.create(
                        escuela=escuela,
                        fecha_pedido=fecha,
                        ne=ne,
                        id_hardware=id_hardware,
                        marca_de_arranque=marca_de_arranque,
                        estado=estadoPendiente,
                        tpmdata=tpmdata,
                        ma_hexa=ma_hexa
                    )
                    cantidad_de_paquetes_creados += 1

        return Response({
            "paquetes": cantidad_de_paquetes_creados
        })

class PermissionViewSet(viewsets.ModelViewSet):
    page_size = 2000
    resource_name = 'permission'
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    resource_name = 'groups'
