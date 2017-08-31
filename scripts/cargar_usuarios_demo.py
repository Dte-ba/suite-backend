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

def crear_usuario_de_prueba(email, nombre, grupo, region=1):
    default_pass = "asdasd123"
    print("Creando usuario %s" %(email))
    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        user = User.objects.create_superuser(email, email=email, password=default_pass)

    user.save()
    perfil = models.Perfil.objects.get(user=user)
    perfil.nombre = 'demo'
    perfil.apellido = nombre

    perfil.email = email
    perfil.region = models.Region.objects.get(numero=int(region))

    perfil.definir_grupo_usando_nombre(grupo)

    #perfil.cargo = models.Cargo.objects.get(nombre=cargo)
    perfil.save()

crear_usuario_de_prueba('admin', 'Admin', 'Administrador')
crear_usuario_de_prueba('coordinador', 'Coordinador', 'Coordinador', region=1)
crear_usuario_de_prueba('facilitador', 'Facilitador', 'Facilitador', region=1)
crear_usuario_de_prueba('referente', 'Referente', 'Referente', region=1)
crear_usuario_de_prueba('administracion', 'Administración', 'Administracion', region=1)
crear_usuario_de_prueba('invitado', 'Invitado', 'Invitado', region=1)
