# coding: utf-8
from __future__ import unicode_literals
from rest_framework import viewsets

from escuelas import models, serializers


class ComentarioDeTareaViewSet(viewsets.ModelViewSet):
    resource_name = 'comentario-de-tarea'
    queryset = models.ComentarioDeTarea.objects.all()
    serializer_class = serializers.ComentarioDeTareaSerializer