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
    search_fields = ['cue', 'nombre']
    filter_fields = ['localidad__distrito__region__numero']

    def get_queryset(self):
        queryset = models.Escuela.objects.all()
        query = self.request.query_params.get('query', None)

        if query:
            filtro_cue = Q(cue__icontains=query)
            filtro_nombre = Q(nombre__icontains=query)

            queryset = queryset.filter(filtro_cue | filtro_nombre)

        return queryset

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = models.Contacto.objects.all()
    serializer_class = serializers.ContactoSerializer

class EventoViewSet(viewsets.ModelViewSet):
    resource_name = 'eventos'
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer

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
    resource_name = 'comentarioDeTarea'
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
