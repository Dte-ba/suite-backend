# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class CargoEscolar(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Cargo: " + self.nombre

    class Meta:
        db_table = 'cargosEscolares'
        verbose_name_plural = 'cargosEscolares'

    class JSONAPIMeta:
        resource_name = "cargosEscolares"
