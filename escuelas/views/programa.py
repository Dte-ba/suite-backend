# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class ProgramaViewSet(viewsets.ModelViewSet):
    queryset = models.Programa.objects.all()
    serializer_class = serializers.ProgramaSerializer