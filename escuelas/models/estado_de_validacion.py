# coding: utf-8
from django.db import models

class EstadoDeValidacion(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Estado: " + self.nombre

    class Meta:
        db_table = 'estadosDeValidacion'
        verbose_name_plural = 'estadosDeValidacion'
