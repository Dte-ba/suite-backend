# coding: utf-8
from __future__ import unicode_literals
import base64
import os
import subprocess
import uuid

import xlwt
from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response

from escuelas import models, serializers


class EventoViewSet(viewsets.ModelViewSet):
    resource_name = 'eventos'
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['escuela__nombre', 'escuela__cue', 'titulo']
    filter_fields = ['escuela__localidad', 'escuela__localidad__distrito', "responsable__id"]
    ordering_fields = ['titulo', 'fecha', 'escuela_id', 'escuela__localidad__distrito__region__numero', 'distrito', 'responsable', 'requiere_traslado']

    def get_queryset(self):
        queryset = self.queryset
        query = self.request.query_params.get('query', None)

        filtro_desde = self.request.query_params.get('desde', None)
        filtro_hasta = self.request.query_params.get('hasta', None)
        filtro_region = self.request.query_params.get('escuela__localidad__distrito__region__numero', None)
        filtro_perfil = self.request.query_params.get('perfil', None)

        if filtro_desde:
            filtro = Q(fecha__gte=filtro_desde)
            queryset = queryset.filter(filtro)

        if filtro_hasta:
            filtro = Q(fecha_fin__lte=filtro_hasta)
            queryset = queryset.filter(filtro)

        if filtro_perfil:
            usuario = models.Perfil.objects.get(id=filtro_perfil)
            filtro = Q(responsable=usuario) | Q(acompaniantes=usuario)
            queryset = queryset.filter(filtro)
        else:
            if filtro_region:
                filtro = Q(escuela__localidad__distrito__region__numero=filtro_region) | Q(escuela__cue=60000000)
                queryset = queryset.filter(filtro)

        if query:
            filtro_escuela = Q(escuela__nombre__icontains=query)
            filtro_escuela_cue = Q(escuela__cue__icontains=query)

            queryset = queryset.filter(filtro_escuela | filtro_escuela_cue | Q(escuela__cue=60000000))

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
