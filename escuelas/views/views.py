# coding: utf-8
from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from escuelas import serializers
from escuelas import models

from rest_framework_json_api.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.views.generic import DetailView
from easy_pdf.views import PDFTemplateResponseMixin, PDFTemplateView


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


class ContactoViewSet(viewsets.ModelViewSet):
    queryset = models.Contacto.objects.all()
    serializer_class = serializers.ContactoSerializer


class RegionViewSet(viewsets.ModelViewSet):
    resource_name = 'regiones'
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    #pagination_class = LargeResultsSetPagination


class DistritoViewSet(viewsets.ModelViewSet):
    resource_name = 'distrito'
    queryset = models.Distrito.objects.all()
    serializer_class = serializers.DistritoSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre']
    filter_fields = ['nombre', 'region']

class LocalidadViewSet(viewsets.ModelViewSet):
    resource_name = 'localidad'

    queryset = models.Localidad.objects.all()
    serializer_class = serializers.LocalidadSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['nombre']
    filter_fields = ['nombre', 'distrito']


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


class EstadoDePaqueteViewSet(viewsets.ModelViewSet):
    queryset = models.EstadoDePaquete.objects.all()
    serializer_class = serializers.EstadoDePaqueteSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    page_size = 2000
    resource_name = 'permission'
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    resource_name = 'groups'
