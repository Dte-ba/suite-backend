from __future__ import unicode_literals

from django.db import models

class Escuela(models.Model):
    cue = CharField(max_length=8, db_index=True)
    nombre = CharField(max_length=100)
    telefono = CharField(max_length=100)
    direccion = CharField(max_length=200)
    lat = CharField(max_length=100)
    lon = CharField(max_length=100)

    class Meta:
        db_table = 'escuelas'

class Contacto(models.Model):
    nombre = CharField(max_length=200)
    telefono_particular = CharField(max_length=100)
    telefono_celular = CharField(max_length=100)
    horario = CharField(max_length=100)
    email = EmailField(max_length=254)

    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)

    class Meta:
        db_table = 'contactos'
