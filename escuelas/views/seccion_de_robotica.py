# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class SeccionDeRoboticaViewSet(viewsets.ModelViewSet):
    queryset = models.SeccionDeRobotica.objects.all()
    serializer_class = serializers.SeccionDeRoboticaSerializer
