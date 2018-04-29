# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class ModalidadViewSet(viewsets.ModelViewSet):
    resource_name = 'modalidad'
    queryset = models.Modalidad.objects.all()
    serializer_class = serializers.ModalidadSerializer