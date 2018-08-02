# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class CursoDeRobotica(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'cursosDeRobotica'
        verbose_name_plural = 'cursosDeRobotica'

    class JSONAPIMeta:
        resource_name = "cursos-de-robotica"
