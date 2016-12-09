# coding: utf-8
from django.db import models

class Escuela(models.Model):
    cue = models.CharField(max_length=8, db_index=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'escuelas'
