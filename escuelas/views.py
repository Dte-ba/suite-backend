# coding: utf-8
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets
import serializers
import models

def home(request):
    return HttpResponse("Bienvenido a la API de SUITE, ingrese en <a href='/api'>/api</a> o <a href='/admin'>/admin</a> para más detalles.")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

class EscuelaViewSet(viewsets.ModelViewSet):
    queryset = models.Escuela.objects.all()
    serializer_class = serializers.EscuelaSerializer

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = models.Contacto.objects.all()
    serializer_class = serializers.ContactoSerializer
