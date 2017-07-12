# coding: utf-8
from django.db import models

class PrioridadTarea(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Prioridad: " + self.nombre

    class Meta:
        db_table = 'prioridades'
        verbose_name_plural = 'prioridades'

    class JSONAPIMeta:
        resource_name = "prioridades"
