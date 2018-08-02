# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class TallerDeRoboticaViewSet(viewsets.ModelViewSet):
    queryset = models.TallerDeRobotica.objects.all()
    serializer_class = serializers.TallerDeRoboticaSerializer
