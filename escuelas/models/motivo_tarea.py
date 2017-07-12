# coding: utf-8
from django.db import models

class MotivoTarea(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Motivo: " + self.nombre

    class Meta:
        db_table = 'motivosDeTareas'
        verbose_name_plural = 'motivosDeTareas'

    class JSONAPIMeta:
        resource_name = "motivosDeTareas"
