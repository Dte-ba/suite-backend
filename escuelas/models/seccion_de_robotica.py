# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class SeccionDeRobotica(models.Model):
    nombre = models.CharField(max_length=10)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'seccionesDeRobotica'
        verbose_name_plural = 'Secciones (Robotica)'

    class JSONAPIMeta:
        resource_name = "secciones-de-robotica"
