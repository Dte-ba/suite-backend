# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class MotivoDeConformacionViewSet(viewsets.ModelViewSet):
    resource_name = 'motivos-de-conformacion'
    queryset = models.MotivoDeConformacion.objects.all()
    serializer_class = serializers.MotivoDeConformacionSerializer