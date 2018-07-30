# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class RolEnRobotica(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, default=None, blank=True, null=True)

    def __unicode__(self):
        return u"Rol: " + self.nombre + "(" + self.descripcion + ")"

    class Meta:
        db_table = 'roles_en_robotica'
        verbose_name_plural = 'roles_en_robotica'

    class JSONAPIMeta:
        resource_name = "roles_en_robotica"
