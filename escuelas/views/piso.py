# coding: utf-8
import base64
import os
import uuid

from django.core.files import File
from rest_framework import viewsets

from escuelas import models, serializers


class PisoViewSet(viewsets.ModelViewSet):
    queryset = models.Piso.objects.all()
    serializer_class = serializers.PisoSerializer

    def perform_update(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_la_llave(serializer)

    def perform_create(self, serializer):
        return self.guardar_modelo_teniendo_en_cuenta_la_llave(serializer)

    def guardar_modelo_teniendo_en_cuenta_la_llave(self, serializer):
        instancia = serializer.save()
        llave = self.request.data.get('llave', None)

        if llave and isinstance(llave, dict):
            nombre = llave['name']
            contenido = llave['contenido']

            archivo_temporal = self.guardar_archivo_temporal(nombre, contenido)

            reopen = open(archivo_temporal, "rb")
            django_file = File(reopen)

            instancia.llave.save('llave.zip', django_file, save=False)

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