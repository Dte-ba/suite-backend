# coding: utf-8
from django.db import models

class TipoDeGestion(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'tiposDeGestion'
        verbose_name_plural = 'tiposDeGestion'

    class JSONAPIMeta:
        resource_name = "tiposDeGestion"
