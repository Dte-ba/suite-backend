# coding: utf-8
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from escuelas import models, serializers


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