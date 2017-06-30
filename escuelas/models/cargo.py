# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Cargo(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __unicode__(self):
        return u"Cargo: " + self.nombre + "(" + self.descripcion + ")"

    class Meta:
        db_table = 'cargos'
        verbose_name_plural = 'cargos'

    class JSONAPIMeta:
        resource_name = "cargos"
