# coding: utf-8
from __future__ import unicode_literals
import xlwt
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from escuelas import models, serializers


class EscuelaViewSet(viewsets.ModelViewSet):
    queryset = models.Escuela.objects.all()
    serializer_class = serializers.EscuelaSerializer
    filter_backends = [SearchFilter]
    search_fields = ['cue', 'nombre', 'localidad__distrito__nombre', 'localidad__nombre']

    def get_queryset(self):
        #solo_padre = Q(padre__isnull=True)
        #queryset = models.Escuela.objects.filter(solo_padre)

        queryset = models.Escuela.objects.all()

        query = self.request.query_params.get('query', None)

        filtro_conformada = self.request.query_params.get('conformada')
        filtro_region = self.request.query_params.get('localidad__distrito__region__numero')
        filtro_programa = self.request.query_params.get('programa')
        filtro_programa_in = self.request.query_params.get('programa_in')
        filtro_modalidad = self.request.query_params.get('modalidad')
        filtro_nivel = self.request.query_params.get('nivel')
        filtro_nivel_nombre = self.request.query_params.get('nivel__nombre')
        filtro_tipo_de_gestion = self.request.query_params.get('tipoDeGestion')
        filtro_piso = self.request.query_params.get('piso')
        filtro_llave = self.request.query_params.get('llave')
        filtro_distrito = self.request.query_params.get('distrito')
        filtro_localidad = self.request.query_params.get('localidad')

        filtro_sort = self.request.query_params.get('sort')

        if filtro_region:
            filtro = Q(localidad__distrito__region__numero=filtro_region) | Q(cue=60000000)
            queryset = queryset.filter(filtro)

        if filtro_modalidad:
            filtro = Q(modalidad=filtro_modalidad)
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

        if filtro_programa_in:
            filtro_in = int(filtro_programa_in)
            filtro = Q(programas=filtro_in)
            queryset = queryset.filter(filtro)

        if filtro_nivel:
            filtro = Q(nivel=filtro_nivel)
            queryset = queryset.filter(filtro)

        if filtro_nivel_nombre:
            filtro = Q(nivel__nombre=filtro_nivel_nombre)
            queryset = queryset.filter(filtro)

        if filtro_tipo_de_gestion:
            filtro = Q(tipo_de_gestion=filtro_tipo_de_gestion)
            queryset = queryset.filter(filtro)

        if filtro_piso:
            if filtro_piso == 'funcionando':
                filtro = Q(piso__estado=True)
            else:
                filtro = Q(piso__estado=False)

            queryset = queryset.filter(filtro)

        if filtro_llave:
            if filtro_llave == 'sin-llave':
                filtro = Q(piso__llave='')
            else:
                filtro = ~Q(piso__llave='')

            queryset = queryset.filter(filtro)

        if filtro_distrito:
            filtro = Q(localidad__distrito=filtro_distrito)
            queryset = queryset.filter(filtro)

        if filtro_localidad:
            filtro = Q(localidad=filtro_localidad)
            queryset = queryset.filter(filtro)


        if query:
            filtro_cue = Q(cue__icontains=query)
            filtro_nombre = Q(nombre__icontains=query)
            filtro_localidad = Q(localidad__nombre__icontains=query)
            filtro_distrito = Q(localidad__distrito__nombre__icontains=query)
            filtro_nivel = Q(nivel__nombre__icontains=query)

            queryset = queryset.filter(filtro_cue | filtro_nombre | filtro_distrito | filtro_localidad | filtro_nivel)

        if filtro_sort:
            queryset = queryset.order_by(filtro_sort)

        return queryset

    @list_route(methods=['get'])
    def estadistica(self, request):
        queryset = models.Escuela.objects.filter(padre__isnull=True)
        filtro_region = self.request.query_params.get('localidad__distrito__region__numero')
        filtro_nivel = self.request.query_params.get('nivel')

        if filtro_region:
            filtro = Q(localidad__distrito__region__numero=filtro_region) | Q(cue=60000000)
            queryset = queryset.filter(filtro)

        if filtro_nivel:
            queryset = queryset.filter(nivel=filtro_nivel)

        estadisticas = {
            "total": queryset.count(),
            "abiertas": queryset.filter(estado=True).count(),
            "cerradas": queryset.filter(estado=False).count(),
            "pisoRoto": queryset.filter(piso__estado=False).count(),
            "pisoFuncionando": queryset.filter(piso__estado=True).count(),
            "conLlave": queryset.filter(Q(piso__llave='') & Q(programas__nombre="Conectar Igualdad")).count(),
            "sinLlave": queryset.filter(Q(piso__llave='') & Q(programas__nombre="Conectar Igualdad")).count(),
            "conectarIgualdad": queryset.filter(programas__nombre="Conectar Igualdad").count(),
            "pad": queryset.filter(programas__nombre="PAD").count(),
            "responsabilidadEmpresarial": queryset.filter(programas__nombre="Responsabilidad Empresarial").count(),
            "primariaDigital": queryset.filter(programas__nombre="Primaria Digital").count(),
            "escuelasDelFuturo": queryset.filter(programas__nombre="Escuelas del Futuro").count(),
            "conformadas": models.Escuela.objects.filter(padre__isnull=False).count(),
            "validaciones": models.Escuela.objects.filter(validaciones__estado__nombre="Aprobada").count()
        }
        return Response(estadisticas)

    @list_route(methods=['get'])
    def escuelas_por_programa(self,request):
        queryset = models.Escuela.objects.filter(padre__isnull=True)
        filtro_region = self.request.query_params.get('localidad__distrito__region__numero')

        if filtro_region:
            filtro = Q(localidad__distrito__region__numero=filtro_region) | Q(cue=60000000)
            queryset = queryset.filter(filtro)

        totalDeEscuelas = queryset.count()

        # Querysets por programa
        conectarIgualdad = queryset.filter(programas__nombre="Conectar Igualdad").count()
        responsabilidadEmpresarial = queryset.filter(programas__nombre="Responsabilidad Empresarial").count()
        primariaDigital = queryset.filter(programas__nombre="Primaria Digital").count()
        escuelasDelFuturo = queryset.filter(programas__nombre="Escuelas del Futuro").count()
        planNacionalDeConectividadEscolar = queryset.filter(programas__nombre="Plan Nacional de Conectividad Escolar").count()

        escuelas_por_programa = [
            {
                "name": "Conectar Igualdad",
                "count": conectarIgualdad
            },
            {
                "name": "Responsabilidad Empresarial",
                "count": responsabilidadEmpresarial
            },
            {
                "name": "Primaria Digital",
                "count": primariaDigital
            },
            {
                "name": "Escuelas del Futuro",
                "count": escuelasDelFuturo
            },
            {
                "name": "Plan Nacional de Conectividad Escolar",
                "count": planNacionalDeConectividadEscolar
            }
        ]

        return Response(escuelas_por_programa)

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
        escuelas = self.get_queryset()
        filas = []

        for escuela in escuelas:
            nombre = escuela.nombre
            cue = escuela.cue
            direccion = escuela.direccion
            region = escuela.localidad.distrito.region.numero
            localidad = escuela.localidad.nombre
            distrito = escuela.localidad.distrito.nombre

            if escuela.modalidad:
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

        # Escribir los headers
        for col_num in range(len(columns)):
            ws.write(0, col_num, columns[col_num], font_style)

        ws.col(0).width = 256 * 12
        ws.col(1).width = 256 * 12
        font_style = xlwt.XFStyle()

        for (indice, fila) in enumerate(escuelas):
            for (indice_columna, columna) in enumerate(fila):
                ws.write(indice+1, indice_columna, columna, font_style)

        wb.save(response)
        return response
