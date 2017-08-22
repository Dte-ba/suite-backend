# coding: utf-8
from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group, Permission

from rest_framework.filters import SearchFilter
from rest_framework.filters import DjangoFilterBackend

from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route

import serializers
import models

import datetime

#
# class LargeResultsSetPagination(pagination.PageNumberPagination):
#     page_size = 1000
#     page_size_query_param = 'page_size'
#     max_page_size = 10000


def home(request):
    return render(request, 'home.html')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

class EscuelaViewSet(viewsets.ModelViewSet):
    queryset = models.Escuela.objects.all()
    serializer_class = serializers.EscuelaSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['cue', 'nombre', 'localidad__nombre', 'nivel__nombre', 'programas__nombre']
    filter_fields = ['localidad__distrito__region__numero', 'conformada']

    def get_queryset(self):
        #solo_padre = Q(padre__isnull=True)
        #queryset = models.Escuela.objects.filter(solo_padre)

        queryset = models.Escuela.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_cue = Q(cue__icontains=query)
            filtro_nombre = Q(nombre__icontains=query)
            filtro_localidad = Q(localidad__nombre__icontains=query)
            filtro_nivel = Q(nivel__nombre__icontains=query)
            filtro_programas = Q(programas__nombre__icontains=query)

            queryset = queryset.filter(filtro_cue | filtro_nombre | filtro_localidad | filtro_nivel | filtro_programas)

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
        }
        return Response(estadisticas)

    @detail_route(methods=['post'])
    def conformar(self, request, pk=None):
        escuela_padre = self.get_object()

        id_escuela = int(request.data['escuela_que_se_absorbera'][0])
        id_motivo = int(request.data['motivo_id'][0])

        escuela = models.Escuela.objects.get(id=id_escuela)
        motivo = models.MotivoDeConformacion.objects.get(id=id_motivo)

        escuela_padre.conformar_con(escuela, motivo)
        return Response({'fechaConformacion': escuela.fechaConformacion})

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = models.Contacto.objects.all()
    serializer_class = serializers.ContactoSerializer

class EventoViewSet(viewsets.ModelViewSet):
    resource_name = 'eventos'
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['escuela__nombre', 'escuela__cue', 'responsable__apellido', 'responsable__dni']
    filter_fields = ['escuela__cue']

    def get_queryset(self):
        queryset = models.Evento.objects.all()
        query = self.request.query_params.get('query', None)
        informe = self.request.query_params.get('informe', None)
        start_date = self.request.query_params.get('inicio', None)
        end_date = self.request.query_params.get('fin', None)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)
            filtro_responsable_apellido = Q(responsable__apellido__icontains=query)
            filtro_responsable_dni = Q(responsable__dni=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue | filtro_responsable_apellido | filtro_responsable_dni)

        if informe:

            # start_date = datetime.date(2017, 8, 1)
            # end_date = datetime.date(2017, 8, 31)
            filtro_responsable = Q(responsable__dni=informe)


            queryset = queryset.filter(filtro_responsable, fecha__range=(start_date, end_date))
            # queryset = queryset.filter(filtro_responsable)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        estadisticas = {
            "total": models.Evento.objects.all().count(),
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


class RegionViewSet(viewsets.ModelViewSet):
    resource_name = 'regiones'
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    #pagination_class = LargeResultsSetPagination

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = models.Perfil.objects.all()
    resource_name = 'perfiles'
    serializer_class = serializers.PerfilSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre', 'apellido', 'dni', 'cargo__nombre']
    filter_fields = ['region__numero']

    def get_queryset(self):
        queryset = self.queryset
        query = self.request.query_params.get('query', None)

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
            "enDTE": models.Perfil.objects.filter(region__numero=27).count(),
            "enTerritorio": models.Perfil.objects.all().exclude(region__numero=27).count(),
        }
        return Response(estadisticas)

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
            'idPerfil': perfil.id
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
    #pagination_class = LargeResultsSetPagination

class ProgramaViewSet(viewsets.ModelViewSet):
    resource_name = 'programa'
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
    resource_name = 'piso'
    queryset = models.Piso.objects.all()
    serializer_class = serializers.PisoSerializer

class CargoEscolarViewSet(viewsets.ModelViewSet):
    resource_name = 'cargoEscolar'
    queryset = models.CargoEscolar.objects.all()
    serializer_class = serializers.CargoEscolarSerializer

class ComentarioDeTareaViewSet(viewsets.ModelViewSet):
    resource_name = 'comentarioDeTareas'
    queryset = models.ComentarioDeTarea.objects.all()
    serializer_class = serializers.ComentarioDeTareaSerializer

class MotivoDeTareaViewSet(viewsets.ModelViewSet):
    resource_name = 'motivoDeTareas'
    queryset = models.MotivoDeTarea.objects.all()
    serializer_class = serializers.MotivoDeTareaSerializer

class EstadoDeTareaViewSet(viewsets.ModelViewSet):
    resource_name = 'estadoDeTareas'
    queryset = models.EstadoDeTarea.objects.all()
    serializer_class = serializers.EstadoDeTareaSerializer

class PrioridadDeTareaViewSet(viewsets.ModelViewSet):
    resource_name = 'prioridadDeTareas'
    queryset = models.PrioridadDeTarea.objects.all()
    serializer_class = serializers.PrioridadDeTareaSerializer

class TareaViewSet(viewsets.ModelViewSet):
    queryset = models.Tarea.objects.all()
    serializer_class = serializers.TareaSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['titulo', 'fechaDeAlta']
    filter_fields = ['autor__nombre']

    def get_queryset(self):
        queryset = models.Tarea.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_titulo = Q(titulo__icontains=query)
            filtro_fechaDeAlta = Q(fechaDeAlta__icontains=query)

            queryset = queryset.filter(filtro_titulo | filtro_fechaDeAlta)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        estadisticas = {
            "total": models.Tarea.objects.all().count(),
            "pendientes": models.Tarea.objects.filter(estadoDeTarea__nombre="Abierto").count(),
            "enProgreso": models.Tarea.objects.filter(estadoDeTarea__nombre="En Progreso").count(),
            "prioridadAlta": models.Tarea.objects.filter(prioridadDeTarea__nombre="Alta").exclude(estadoDeTarea__nombre="Cerrado").count(),
        }
        return Response(estadisticas)

class CategoriaDeEventoViewSet(viewsets.ModelViewSet):
    resource_name = 'categoriasDeEventos'
    queryset = models.CategoriaDeEvento.objects.all()
    serializer_class = serializers.CategoriaDeEventoSerializer

class MotivoDeConformacionViewSet(viewsets.ModelViewSet):
    resource_name = 'motivosDeConformacion'
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
    filter_fields = ['escuela__nombre']

    def get_queryset(self):
        queryset = models.Validacion.objects.all()
        query = self.request.query_params.get('query', None)

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


class EstadoDePaqueteViewSet(viewsets.ModelViewSet):
    queryset = models.EstadoDePaquete.objects.all()
    serializer_class = serializers.EstadoDePaqueteSerializer

class PaqueteViewSet(viewsets.ModelViewSet):
    queryset = models.Paquete.objects.all()
    serializer_class = serializers.PaqueteSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['escuela__nombre', 'escuela__cue', 'estado__nombre', 'idHardware', 'ne', 'escuela__piso__serie']
    filter_fields = ['escuela__localidad__distrito__region__numero']

    def get_queryset(self):
        queryset = models.Paquete.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)
            filtro_estado = Q(estado__nombre__icontains=query)
            filtro_idHardware = Q(idHardware__icontains=query)
            filtro_ne = Q(ne__icontains=query)
            filtro_serie = Q(escuela__piso__serie__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue | filtro_estado | filtro_idHardware | filtro_ne | filtro_serie)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        estadisticas = {
            "total": models.Paquete.objects.all().count(),
            "pendientes": models.Paquete.objects.filter(estado__nombre="Pendiente").count(),
            "objetados": models.Paquete.objects.filter(estado__nombre="Objetado").count(),
            "enviados": models.Paquete.objects.filter(estado__nombre="EducAr").count(),
            "devueltos": models.Paquete.objects.filter(estado__nombre="Devuelto").count(),
        }
        return Response(estadisticas)


class PermissionViewSet(viewsets.ModelViewSet):
    page_size = 2000
    resource_name = 'permission'
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
