# coding: utf-8
from django.db import models

class Localidad(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Localidad: " + self.nombre

    class Meta:
        db_table = 'localidades'
        verbose_name_plural = 'localidades'

    class JSONAPIMeta:
        resource_name = "localidades"
