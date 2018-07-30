# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class RolEnRoboticaViewSet(viewsets.ModelViewSet):
    resource_name = 'rol_en_robotica'
    queryset = models.RolEnRobotica.objects.all()
    serializer_class = serializers.RolEnRoboticaSerializer
