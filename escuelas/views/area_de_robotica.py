# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class AreaDeRoboticaViewSet(viewsets.ModelViewSet):
    queryset = models.AreaDeRobotica.objects.all()
    serializer_class = serializers.AreaDeRoboticaSerializer
