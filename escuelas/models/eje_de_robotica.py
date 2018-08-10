# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class EjeDeRobotica(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'ejesDeRobotica'
        verbose_name_plural = 'Ejes (Robotica)'

    class JSONAPIMeta:
        resource_name = "ejes-de-robotica"
