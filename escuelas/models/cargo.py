# coding: utf-8
from django.db import models

class Cargo(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Cargo: " + self.nombre

    class Meta:
        db_table = 'cargos'
        verbose_name_plural = 'cargos'

    class JSONAPIMeta:
        resource_name = "cargos"
