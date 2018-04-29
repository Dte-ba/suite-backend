# coding: utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import Group
from rest_framework import viewsets

from escuelas import serializers


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    resource_name = 'groups'