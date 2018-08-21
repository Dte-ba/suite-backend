# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from escuelas import models, serializers


class RegionViewSet(viewsets.ModelViewSet):
    resource_name = 'regiones'
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer

    filter_backends = [DjangoFilterBackend]
    filter_fields = ['numero']
