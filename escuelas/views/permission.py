# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import Permission
from rest_framework import viewsets

from escuelas import serializers


class PermissionViewSet(viewsets.ModelViewSet):
    page_size = 2000
    resource_name = 'permission'
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer