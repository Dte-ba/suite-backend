# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers
from django_filters.rest_framework import DjangoFilterBackend

class TallerDeRoboticaViewSet(viewsets.ModelViewSet):
    queryset = models.TallerDeRobotica.objects.all()
    serializer_class = serializers.TallerDeRoboticaSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['area__id']
