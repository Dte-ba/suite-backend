# coding: utf-8
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets

import serializers

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

def home(request):
    return HttpResponse("Bienvenido a la API de SUITE, ingrese en /api o /admin para más detalles.")
