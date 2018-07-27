# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class AplicacionViewSet(viewsets.ModelViewSet):
    queryset = models.Aplicacion.objects.all()
    serializer_class = serializers.AplicacionSerializer
