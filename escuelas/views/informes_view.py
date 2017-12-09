# coding: utf-8
import re

from django.http import HttpResponse
from django.template import loader
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
import easy_pdf

from escuelas.models import Perfil
from escuelas.serializers import EventoSerializer, PerfilSerializer

FORMATO_FECHA = "\d{4}-\d{2}-\d{2}"

from rest_framework.decorators import authentication_classes, permission_classes


class InformesViewSet(viewsets.ViewSet):

    @authentication_classes([])
    @permission_classes([])
    def list(self, request):
        perfil_id = self.request.query_params.get('perfil_id', None)
        desde = self.request.query_params.get('desde', None)
        hasta = self.request.query_params.get('hasta', None)
        formato = self.request.query_params.get('formato', u'json')
        imprimir = self.request.query_params.get('imprimir', False)

        if None in [perfil_id, desde, hasta]:
            return Response({
                'error': "No han especificado todos los argumentos: perfil_id, desde y hasta."
            })

        if not re.match(FORMATO_FECHA, desde) or not re.match(FORMATO_FECHA, hasta):
            return Response({
                'error': "Las fechas están en formato incorrecto, deben ser YYYY-MM-DD."
            })

        perfil = Perfil.objects.get(id=perfil_id)
        perfil_serializado = PerfilSerializer(perfil, context={'request': request}).data

        eventos = perfil.obtener_eventos_por_fecha(desde, hasta)
        eventos_serializados = EventoSerializer(eventos, many=True).data


        if formato == u'json':
            data = {
                'perfil': perfil_serializado,
                'eventos': eventos_serializados
            }
            return Response(data)
        elif formato in ['html', 'pdf']:
            template = loader.get_template('informe.html')
            contexto = {
                "perfil": perfil,
                "eventos": eventos,
                "desde": self._formatear_fecha(desde),
                "hasta": self._formatear_fecha(hasta),
                "imprimir": imprimir,
                "pdf": (formato == 'html')
            }

            if formato == 'html':
                return HttpResponse(template.render(contexto, request))
            else:
                return easy_pdf.rendering.render_to_pdf_response(request, "informe.html", contexto)
        else:
            return Response({
                    'error': u'Formato %s no reconocido' %(formato)
                })

    def _formatear_fecha(self, fecha_como_string):
        import datetime
        return datetime.datetime.strptime(fecha_como_string, "%Y-%m-%d").strftime("%d/%m/%Y")
