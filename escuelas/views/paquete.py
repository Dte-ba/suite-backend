# coding: utf-8
from __future__ import unicode_literals
import json
import re

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from escuelas import models, serializers


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
    def export_raw(self, request):
        # NOTA: solo se usa internamente en los tests de paquetes.
        inicio = self.request.query_params.get('inicio', None)
        fin = self.request.query_params.get('fin', None)
        estadoPedido = self.request.query_params.get('estado', None)

        data = models.Paquete.obtener_paquetes_para_exportar(inicio, fin, estadoPedido)
        data['llaves'] = [str(llave) for llave in data['llaves']]
        return Response(data)

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
            objeto_estado_pendiente = models.EstadoDePaquete.objects.get(nombre="Pendiente")
            objeto_estado_educar = models.EstadoDePaquete.objects.get(nombre="EducAr")
            objeto_paquete = models.Paquete.objects.filter(ne=ne, id_hardware=id_hardware, marca_de_arranque=marca_de_arranque, estado__in=[objeto_estado_pendiente, objeto_estado_educar])

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
