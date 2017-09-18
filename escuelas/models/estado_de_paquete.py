# coding: utf-8
from django.db import models

class EstadoDePaquete(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Estado: " + self.nombre

    class Meta:
        db_table = 'estadosDePaquete'
        verbose_name_plural = 'estadosDePaquete'

    class JSONAPIMeta:
        resource_name = 'estados-de-paquete'
