# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class CategoriaDeEvento(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'categoriasDeEventos'
        verbose_name_plural = 'categoriasDeEventos'

    class JSONAPIMeta:
        resource_name = "categorias-de-eventos"
