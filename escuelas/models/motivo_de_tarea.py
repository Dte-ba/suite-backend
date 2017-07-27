# coding: utf-8
from django.db import models

class MotivoDeTarea(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Motivo: " + self.nombre

    class Meta:
        db_table = 'motivosDeTarea'
        verbose_name_plural = 'motivosDeTarea'

    class JSONAPIMeta:
        resource_name = "motivosDeTarea"
