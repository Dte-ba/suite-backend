# coding: utf-8
from __future__ import unicode_literals
import xlwt
from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from escuelas import models, serializers


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