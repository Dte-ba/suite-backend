# coding: utf-8
from django.db import models

class EstadoDeTarea(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Estado: " + self.nombre

    class Meta:
        db_table = 'estadosDeTarea'
        verbose_name_plural = 'estadosDeTarea'
