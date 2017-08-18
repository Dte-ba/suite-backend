# coding: utf-8
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from rest_framework.filters import SearchFilter
from rest_framework.filters import DjangoFilterBackend

from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route

import serializers
import models

"""
class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000
"""

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
    search_fields = ['escuela__nombre', 'escuela__cue']
    filter_fields = ['escuela__cue']

    def get_queryset(self):
        queryset = models.Evento.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue)

        return queryset

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
    search_fields = ['nombre', 'apellido', 'dni', 'region__numero', 'cargo__nombre']
    filter_fields = ['region__numero']

    def get_queryset(self):
        queryset = models.Perfil.objects.all()
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
            'permisosComoLista': perfil.obtenerListaDePermisos(),
            'permisos': perfil.obtenerPermisosComoDiccionario(),
            'grupos': perfil.obtenerListaDeGrupos(),
            'idPerfil': perfil.id
        }
        return Response(data)

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
    search_fields = ['escuela__nombre', 'escuela__cue', 'estado__nombre']
    filter_fields = ['escuela__nombre']

    def get_queryset(self):
        queryset = models.Paquete.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)
            filtro_estado = Q(estado__nombre__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue | filtro_estado)

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
