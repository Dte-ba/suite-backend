# coding: utf-8
from django.db import models

class PrioridadDeTarea(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Prioridad: " + self.nombre

    class Meta:
        db_table = 'prioridadesDeTarea'
        verbose_name_plural = 'prioridadesDeTarea'

    class JSONAPIMeta:
        resource_name = "prioridadesDeTarea"
