# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class TallerDeRobotica(models.Model):
    nombre = models.CharField(max_length=255)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'talleresDeRobotica'
        verbose_name_plural = 'talleresDeRobotica'

    class JSONAPIMeta:
        resource_name = "talleres-de-robotica"
