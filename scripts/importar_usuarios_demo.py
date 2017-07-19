# coding: utf-8
from __future__ import unicode_literals
import sys
import pprint
import os
import django
import pprint
sys.path.append("..")
sys.path.append(".")
# Configuración inicial de django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "suite.settings")
django.setup()

from escuelas import models
from django.contrib.auth.models import User

def crear_usuario_de_prueba(email, nombre, region=1):
    default_pass = "asdasd123"
    print("Creando usuario %s" %(email))
    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        user = User.objects.create_superuser(email, email=email, password=default_pass)

    user.save()
    perfil = models.Perfil.objects.get(user=user)
    perfil.nombre = nombre

    perfil.email = email
    perfil.region = models.Region.objects.get(numero=int(region))
    #perfil.cargo = models.Cargo.objects.get(nombre=cargo)
    perfil.save()

crear_usuario_de_prueba('admin', 'Admin')
crear_usuario_de_prueba('coordinador', 'Coordinador', region=1)
crear_usuario_de_prueba('facilitador', 'Facilitador', region=1)
