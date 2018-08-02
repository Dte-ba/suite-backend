# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class CursoDeRoboticaViewSet(viewsets.ModelViewSet):
    queryset = models.CursoDeRobotica.objects.all()
    serializer_class = serializers.CursoDeRoboticaSerializer
