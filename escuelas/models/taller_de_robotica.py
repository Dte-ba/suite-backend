# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class TallerDeRobotica(models.Model):
    nombre = models.CharField(max_length=255)
    area = models.ForeignKey('AreaDeRobotica', on_delete=models.CASCADE, related_name='taller_de_robotica', default=None, blank=True, null=True)
    eje = models.ForeignKey('EjeDeRobotica', on_delete=models.CASCADE, related_name='taller_de_robotica', default=None, blank=True, null=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        db_table = 'talleresDeRobotica'
        verbose_name_plural = 'Talleres (Robotica)'

    class JSONAPIMeta:
        resource_name = "talleres-de-robotica"
