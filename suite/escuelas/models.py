from __future__ import unicode_literals
from django.db import models

class Escuela(models.Model):
    cue = models.CharField(max_length=8, db_index=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)

    class Meta:
        db_table = 'escuelas'

class Contacto(models.Model):
    nombre = models.CharField(max_length=200)
    telefono_particular = models.CharField(max_length=100)
    telefono_celular = models.CharField(max_length=100)
    horario = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)

    escuela = models.ForeignKey(Escuela, on_delete=models.CASCADE)

    class Meta:
        db_table = 'contactos'
