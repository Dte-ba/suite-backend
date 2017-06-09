# coding: utf-8
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets

import serializers
import models

def home(request):
    return render(request, 'home.html')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

class EscuelaViewSet(viewsets.ModelViewSet):
    queryset = models.Escuela.objects.all()
    serializer_class = serializers.EscuelaSerializer

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = models.Contacto.objects.all()
    serializer_class = serializers.ContactoSerializer

class EventoViewSet(viewsets.ModelViewSet):
    resource_name = 'eventos'
    queryset = models.Evento.objects.all()
    serializer_class = serializers.EventoSerializer

class RegionViewSet(viewsets.ModelViewSet):
    resource_name = 'regiones'
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer

class PerfilViewSet(viewsets.ModelViewSet):
    resource_name = 'perfiles'
    queryset = models.Perfil.objects.all()
    serializer_class = serializers.PerfilSerializer

    def partial_update(self, request, pk=None):
        #file_obj = request.FILES['demo']
        print(request.data)
        #print(file_obj)
        return viewsets.ModelViewSet.partial_update(self, request, pk)

class MunicipioViewSet(viewsets.ModelViewSet):
    resource_name = 'municipio'
    queryset = models.Municipio.objects.all()
    serializer_class = serializers.MunicipioSerializer
